import logging
import re

from django.db.models import Count, Sum
from django.utils.timesince import timesince
from django.utils.timezone import make_aware, now, utc

from discord.enums import Status
from tabulate import tabulate

from bot.channels.models import Channel
from bot.plugins.base import BasePlugin
from bot.plugins.commands import command
from bot.users.models import Member

from .models import LoggedMessage, GameSession


logger = logging.getLogger(__name__)


class Plugin(BasePlugin):

    has_blocking_io = True

    def on_message(self, message):
        """
        Log the message in the db
        """
        yield from super().on_message(message)

        if message.channel.is_private:
            return

        member = Member.objects.from_message(message)
        channel = Channel.objects.from_message(message)

        n_lines = len(message.content.splitlines())

        logged_message = LoggedMessage.objects.create(
            discord_id=message.id, member=member,
            member_username=message.author.name,
            channel=channel, content=message.content,
            num_lines=n_lines
        )
        if message.mentions:
            logged_message.mentions = Member.objects.from_mentions(message.mentions)

    def on_message_edit(self, before, after):
        yield from super().on_message_edit(before, after)

        logged_message = LoggedMessage.objects.filter(discord_id=before.id).first()
        if not logged_message:
            return

        logged_message.edited_timestamp = make_aware(after.edited_timestamp, utc)
        logged_message.content = after.content
        logged_message.num_lines = len(after.content.splitlines())
        logged_message.save()

    def on_member_update(self, before, after):
        if hasattr(super(), 'on_member_update'):
            yield from super().on_member_update(before, after)

        member = Member.objects.from_discord(after)

        if before.status != after.status and after.status != Status.online:
            member.last_seen = now()
            member.save()

        # started playing a game
        if not before.game and after.game:
            GameSession.objects.create(
                member=member, game=after.game.name,
                start=now()
            )
        # stopped playing
        elif before.game and not after.game:
            try:
                session = GameSession.objects.filter(member=member, game=before.game.name).latest('start')
            except GameSession.DoesNotExist:
                pass
            else:
                session.stop = now()
                session.duration = session.stop - session.start
                session.save()

    @command(help='Show the top 10 posters')
    def stat_messages(self, command):
        yield from command.send_typing()
        queryset = Member.objects.exclude(is_bot=True).annotate(num_messages=Count('messages_authored'))
        top_10 = queryset.order_by('-num_messages')[:10]
        data = [(member.name or str(member), member.num_messages) for member in top_10]
        output = tabulate(data, headers=('User', 'Messages'))
        yield from command.reply("```\n{}\n```".format(output))

    @command(pattern=re.compile(r'(?P<name>.*)', re.IGNORECASE))
    def seen(self, command):
        if command.message.mentions:
            if len(command.message.mentions) > 1:
                yield from command.reply('Supply one user at a time')
                return
            d_member = command.message.mentions[0]
            member = Member.objects.filter(discord_id=d_member.id).first()
            username = d_member.name
        else:
            username = command.args.name
            member = Member.objects.filter(name__iexact=username).first()
            all_members = command.message.channel.server.members
            d_member = next((m for m in all_members if m.name.lower() == username.lower()), None)

        if d_member and d_member.status == Status.online:
            yield from command.reply('{} is currently online'.format(d_member.name))
            if member:
                member.last_seen = now()
                member.save()
            return

        if not member or not member.last_seen:
            yield from command.reply('Haven\'t seen {} (yet)'.format(username))
            return

        if member:
            last_message = member.messages_authored.latest('timestamp')
            reply1 = "{name} was last seen: {last_seen} ago".format(
                name=username,
                last_seen=timesince(member.last_seen)
            )
            reply2 = "The last message was: ```{message}```".format(message=last_message.content)
            yield from command.reply("{}\n{}".format(reply1, reply2))

    @command(help='Shows the most popular games in total play time')
    def stat_games(self, command):
        yield from command.send_typing()
        games = GameSession.objects.filter(duration__isnull=False).values('game').annotate(
            time=Sum('duration'),
            num_players=Count('member', distinct=True)
        ).filter(num_players__gt=1).order_by('-time')[:15]

        def format_delta(delta):
            hours, seconds = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(seconds, 60)
            min_minutes = not hours and not delta.days
            return "{days} days, {hours} hours, {minutes} minutes".format(
                days=delta.days, hours=hours, minutes=max(1, minutes) if min_minutes else minutes)

        data = [
            (game['game'], format_delta(game['time'])) for game in games
        ]
        yield from command.reply("```\n{}\n```".format(tabulate(data, headers=('Game', 'Time'))))
