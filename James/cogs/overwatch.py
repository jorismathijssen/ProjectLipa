"""
overwatch.py - Ask the overwatch wikia a question
Copyright 2016, Guus Beckett reupload.nl
Licensed under the GPL 2.

"""
import wikia
from discord.ext import commands


# title_tag_data = re.compile('<(/?)title( [^>]+)?>', re.IGNORECASE)
# r =requests.get('http://overwatch.wikia.com/wiki/Ana')
class Overwatch:
    """Overwatch wikia functions for the bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def overwatch(self, ctx, *, message: str):
        """
        Search the overwatch wikia for the search term you provided. For example: !overwatch Sombra. Returns: Summary text
        """

        await self.bot.say(await self.searchOverwatchWikia(message))

    @commands.command(pass_context=True)
    async def overwatchwiki(self, ctx, *, message: str):
        """
        Search the overwatch wikia for the search term you provided. For example: !overwatch Sombra. Returns: Link to Wikia Page
        """

        try:
            page = wikia.page("Overwatch", message)
            response = page.url.replace(" ", "%20")
        except:
            response = "Sorry, die kon ik niet vinden :("

        await self.bot.say(response)

    async def searchOverwatchWikia(self, searchQuery):
        try:
            response = wikia.summary("Overwatch", searchQuery)
            if ("REDIRECT" in response):
                response = wikia.summary("Overwatch", response.replace("REDIRECT", ""))
        except:
            response = "Sorry, die kon ik niet vinden :("
        return response


def setup(bot):
    bot.add_cog(Overwatch(bot))
