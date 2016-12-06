import copy
import datetime
import json
import logging
import sys
import traceback
import re
from collections import Counter

import discord
from discord.ext import commands

from cogs.utils import checks
from cogs import ai

description = """
Hello my name is James, how may I help you?
"""

initial_extensions = [
    'cogs.admin',
    'cogs.mod',
    'cogs.api',
    'cogs.translate',
    'cogs.meta',
    'cogs.weather',
    'cogs.playlist'

]

discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.CRITICAL)
log = logging.getLogger()
log.setLevel(logging.INFO)
handler = logging.FileHandler(filename='JamesLog.log', encoding='utf-8', mode='w')
log.addHandler(handler)

help_attrs = dict(hidden=True)

prefix = ['!', '.', '\N{HEAVY EXCLAMATION MARK SYMBOL}']
bot = commands.Bot(command_prefix=prefix, description=description, pm_help=None, help_attrs=help_attrs)


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, 'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author, 'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)
    elif isinstance(error, commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)
        fmt = "Please slowdown " + ctx.message.author.mention + ", this command is on cooldown! Try again in {} minutes and {} seconds".format(
            round(m), round(s))
        await bot.send_message(ctx.message.channel, fmt)


@bot.event
async def on_ready():
    print('Logged in as:')
    print('Username: ' + bot.user.name)
    print('ID: ' + bot.user.id)
    print('------')
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow()
    # game = discord.Game(name='Butler Simulator Deluxe', url='http://reupload.nl', type=1)
    # await bot.change_presence(game=game, status=None, afk=False)


@bot.event
async def on_resumed():
    print('resumed...')


@bot.event
async def on_command(command, ctx):
    bot.commands_used[command.name] += 1
    message = ctx.message
    destination = None
    if message.channel.is_private:
        destination = 'Private Message'
    else:
        destination = '#{0.channel.name} ({0.server.name})'.format(message)

    log.info('{0.timestamp}: {0.author.name} in {1}: {0.content}'.format(message, destination))

@bot.event
async def on_message(message):
    python = bot

    if python == None:
        print('kek')

    if message.author.bot:
        return
    question = re.compile('.*{0}.*\?'.format(bot.user.name))
    laugh = re.compile('\s*([Xx]+[dD]+|([Hh]+[Aa]+)+)')
    oink = re.compile('.*[Kk]nor.*')
    bye = re.compile('^([Bb]ye|[Gg]oodbye|[Gg]tg|[Ss]eeya|[Cc]ya|[Tt]tyl|[Gg]2g|[Gg]night|[Gg]oodnight|[Ll]ater|[Hh]oudoe|[Dd]oei)$')
    haha = re.compile('(haha!?|lol!?)$')
    thanks = re.compile('(.*([Bb]edankt).*|.*([Tt]hank).*([Yy]ou)|.*([Tt]hanks).*).*{0}.*$'.format(bot.user.name))
    msg = ""
    if question.match(message.content):
        msg = ai.eightball()
    elif oink.match(message.content):
        msg = "Wat ben jij een lief varkentje! 🐷"
    elif laugh.match(message.content):
        msg = await ai.laugh()
    elif haha.match(message.content):
        msg = await ai.haha()
    elif thanks.match(message.content):
        msg = ai.thanks()
    elif bye.match(message.content):
        msg = "{0} {1.author.mention}".format(ai.bye(),message)
    if msg != "":
        await bot.send_message(message.channel, msg)

    await bot.process_commands(message)


@bot.command(pass_context=True, hidden=True)
@checks.is_owner()
async def do(ctx, times: int, *, command):
    """Repeats a command a specified number of times."""
    msg = copy.copy(ctx.message)
    msg.content = command
    for i in range(times):
        await bot.process_commands(msg)


def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)


if __name__ == '__main__':
    credentials = load_credentials()
    debug = any('debug' in arg.lower() for arg in sys.argv)
    if debug:
        bot.command_prefix = '$'
        token = credentials.get('debug_token', credentials['token'])
    else:
        token = credentials['token']

    bot.client_id = credentials['client_id']
    bot.commands_used = Counter()
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    bot.run(token)
    handlers = log.handlers[:]
    for hdlr in handlers:
        hdlr.close()
        log.removeHandler(hdlr)
