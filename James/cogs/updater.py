"""
updater.py - update and restart James
Copyright 2016, Guus Beckett reupload.nl
Licensed under the GPL 2.
"""
import os
import subprocess
import sys

from discord.ext import commands

from .utils import checks


class updater:
    """Update functions for the bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=False)
    @checks.admin_or_permissions(manage_server=True)
    async def updateFromGit(self):
        """
           Search the overwatch wikia for the search term you provided. For example: !overwatch Sombra. Returns: Summary text
        """

        await self.bot.say("brb!")
        await self.update()

    async def update(self):
        """ Updates James by pulling the latests commits from
        github and restarting itself"""
        subprocess.call("./cogs/update.sh")
        await self.restart_program()

    async def restart_program(self):
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""
        python = sys.executable
        os.execl(python, python, *sys.argv)


def setup(bot):
    bot.add_cog(updater(bot))
