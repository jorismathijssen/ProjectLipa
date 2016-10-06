import logging
import random
import re

import praw
from django.db.models import F

from bot.channels.models import Channel
from bot.plugins.base import BasePlugin
from bot.plugins.commands import command, Command, PREFIX
from bot.users.decorators import command_passes_test, is_bot_admin, has_channel_permission

from .models import RedditCommand


logger = logging.getLogger(__name__)


def reddit_admin(command):
    message = command.message
    return has_channel_permission(message, 'manage_channels') or is_bot_admin(message)


class Plugin(BasePlugin):

    has_blocking_io = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reddit_bot = praw.Reddit(user_agent=self.options['useragent'])

    def get_nsfw_allowed(self, command):
        """
        Allow NSFW subreddits if:
        * it's a private message with the bot
        * it's a channel explicitly marked as nsfw allowed
        """
        discord_channel = command.message.channel
        if discord_channel.is_private:
            return True
        else:
            channel, _ = Channel.objects.get_or_create(discord_id=discord_channel.id, defaults={
                'name': discord_channel.name
            })
            return channel.allow_nsfw
        return False

    @command(
        pattern=re.compile(r'!?(?P<cmd>.*): (?P<subreddit>.*)', re.IGNORECASE),
        help='Configure a command to show a subreddit submission'
    )
    def add_subreddit(self, command):
        cmd, subreddit = command.args.cmd, command.args.subreddit

        try:
            sr = self.reddit_bot.get_subreddit(subreddit)
            nsfw = sr.over18
        except praw.errors.InvalidSubreddit:
            yield from command.reply('Subreddit `{}` does not exist'.format(subreddit))
            return

        reddit_cmd, created = RedditCommand.objects.get_or_create(
            command=cmd, defaults={'subreddit': subreddit, 'nsfw': nsfw}
        )
        tpl = 'Added %r' if created else 'Command already exists: %r'
        yield from command.reply(tpl % reddit_cmd)

    @command(
        pattern=re.compile(r'(?P<subreddit>[\w]+)', re.IGNORECASE),
        help='Mark a subreddit as NSFW. Specify the **subreddit** without the /r/, not the command.'
    )
    @command_passes_test(reddit_admin)
    def mark_nsfw(self, command):
        sr = command.args.subreddit
        rc = RedditCommand.objects.filter(subreddit=sr, nsfw=False)
        if not rc.exists():
            yield from command.reply('No command configured for {sr}'.format(sr=sr))
            return

        updated = rc.update(nsfw=True)
        yield from command.reply('Marked **{sr}** as NSFW (affected {n} command(s))'.format(sr=sr, n=updated))

    @command(help='Mark this channel as NSFW allowed.')
    @command_passes_test(reddit_admin)
    def allow_nsfw(self, command):
        discord_channel = command.message.channel
        if discord_channel.is_private:
            return

        channel, _ = Channel.objects.get_or_create(
            discord_id=discord_channel.id,
            defaults={'name': discord_channel.name})
        if channel.allow_nsfw:
            yield from command.reply('Channel already allowed NSFW')
            return
        channel.allow_nsfw = True
        channel.save()
        yield from command.reply('NSFW is now allowed')

    @command(help='Lists the command to fetch submissions from a subreddit')
    def list_subreddits(self, command):
        i = 0
        buffer_ = []

        commands = RedditCommand.objects.all()
        allow_nsfw = self.get_nsfw_allowed(command)
        if not allow_nsfw:
            commands = commands.filter(nsfw=False)

        for reddit_cmd in commands:
            i += 1
            line = '{i}. {cmd} ({used}x used)'.format(
                i=i, cmd=reddit_cmd, used=reddit_cmd.times_used
            )
            if reddit_cmd.nsfw:
                line = '{} **NSFW**'.format(line)
            buffer_.append(line)

            if len(buffer_) % 10 == 0:
                yield from command.reply("\n".join(buffer_))
                buffer_ = []

        if len(buffer_):
            yield from command.reply("\n".join(buffer_))

    def on_message(self, message):
        yield from super().on_message(message)

        if not message.content.startswith(PREFIX):
            return

        command = Command(None, for_message=message)
        command.client = self.client

        cmd = message.content[len(PREFIX):]
        try:
            reddit_cmd = RedditCommand.objects.get(command=cmd)
            reddit_cmd.times_used = F('times_used') + 1
            reddit_cmd.save()
        except RedditCommand.DoesNotExist:
            return

        allow_nsfw = self.get_nsfw_allowed(command)
        if reddit_cmd.nsfw and not allow_nsfw:
            yield from command.reply('No NSFW commands allowed here')
            return

        yield from command.send_typing()
        subreddit = self.reddit_bot.get_subreddit(reddit_cmd.subreddit)
        logger.debug('Fetched subreddit %s', reddit_cmd.subreddit)
        submissions = [s for s in subreddit.get_hot(limit=50)]
        submission = random.choice(submissions)
        logger.debug('Picked a submission')
        yield from command.reply(submission.url)
        logger.debug('Sent message')
