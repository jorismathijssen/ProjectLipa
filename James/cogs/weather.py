from urllib.parse import urlencode

import aiohttp
import xmltodict
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Weather:
    """Commands for utilities related to weather"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    async def woeid_search(self, query):
        """
        Find the first Where On Earth ID for the given query. Result is the etree
        node for the result, so that location data can still be retrieved. Returns
        None if there is no result, or the woeid field is empty.
        """
        url = 'http://query.yahooapis.com/v1/public/yql?'

        string = 'select * from geo.places where text="%s"' % query

        f = {'q': string}
        urlendoced = urlencode(f)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' +
                          'Chrome/53.0.2785.143 Safari/537.36'
        }

        async with self.session.get(url=(url + urlendoced), headers=headers) as resp:
            if resp.status == 200:
                parsed = xmltodict.parse(await resp.text()).get('query')
                results = parsed.get('results')
                if results is None or results.get('place') is None:
                    return None
                if type(results.get('place')) is list:
                    return results.get('place')[0]
                return results.get('place')
            else:
                return None

    async def get_temp(self, parsed):
        try:
            condition = parsed['channel']['item']['yweather:condition']
            temp = int(condition['@temp'])
        except (KeyError, ValueError):
            return 'unknown'
        f = round((temp * 1.8) + 32, 2)
        return (u'%d\u00B0C (%d\u00B0F)' % (temp, f))

    async def get_cover(self, parsed):
        try:
            condition = parsed['channel']['item']['yweather:condition']
        except KeyError:
            return 'unknown'
        text = condition['@text']
        # code = int(condition['code'])
        # TODO parse code to get those little icon thingies.
        return text

    async def get_humidity(self, parsed):
        try:
            humidity = parsed['channel']['yweather:atmosphere']['@humidity']
        except (KeyError, ValueError):
            return 'unknown'
        return "Humidity: %s%%" % humidity

    async def get_wind(self, parsed):
        try:
            wind_data = parsed['channel']['yweather:wind']
            kph = float(wind_data['@speed'])
            m_s = float(round(kph / 3.6, 1))
            speed = int(round(kph / 1.852, 0))
            degrees = int(wind_data['@direction'])
        except (KeyError, ValueError):
            return 'unknown'

        if speed < 1:
            description = 'Calm'
        elif speed < 4:
            description = 'Light air'
        elif speed < 7:
            description = 'Light breeze'
        elif speed < 11:
            description = 'Gentle breeze ' + '\N{WIND BLOWING FACE}'
        elif speed < 16:
            description = 'Moderate breeze'
        elif speed < 22:
            description = 'Fresh breeze'
        elif speed < 28:
            description = 'Strong breeze ' + '\N{CLOUD WITH RAIN}'

        elif speed < 34:
            description = 'Near gale'
        elif speed < 41:
            description = 'Gale'
        elif speed < 48:
            description = 'Strong gale'
        elif speed < 56:
            description = 'Storm'
        elif speed < 64:
            description = 'Violent storm ' + '\N{CLOUD WITH LIGHTNING}'
        else:
            description = 'Hurricane ' + '\N{CLOUD WITH TORNADO}'

        if (degrees <= 22.5) or (degrees > 337.5):
            degrees = '\N{UPWARDS BLACK ARROW}'
        elif (degrees > 22.5) and (degrees <= 67.5):
            degrees = '\N{NORTH EAST ARROW}'
        elif (degrees > 67.5) and (degrees <= 112.5):
            degrees = '\N{BLACK RIGHTWARDS ARROW}'
        elif (degrees > 112.5) and (degrees <= 157.5):
            degrees = '\N{SOUTH EAST ARROW}'
        elif (degrees > 157.5) and (degrees <= 202.5):
            degrees = '\N{DOWNWARDS BLACK ARROW}'
        elif (degrees > 202.5) and (degrees <= 247.5):
            degrees = '\N{SOUTH WEST ARROW}'
        elif (degrees > 247.5) and (degrees <= 292.5):
            degrees = '\N{LEFTWARDS BLACK ARROW}'
        elif (degrees > 292.5) and (degrees <= 337.5):
            degrees = '\N{NORTH WEST ARROW}'

        return description + ' ' + str(m_s) + 'm/s (' + degrees + ')'

    @commands.cooldown(2, 120, BucketType.user)
    @commands.command(pass_context=True, hidden=False, aliases=['Weather', 'weer', 'Weer'])
    async def weather(self, ctx, *, location=''):
        """Displays my intro message."""
        author = ctx.message.author
        woeid = ''

        if not location:
            await self.bot.say("I don't know where you live. " +
                               'Give me a location, like .weather London.')
            return
        first_result = await self.woeid_search(location)
        if first_result is not None:
            woeid = first_result.get('woeid')
        if not woeid:
            await self.bot.say("I don't know where that is.")
            return

        url = 'http://query.yahooapis.com/v1/public/yql?'
        string = 'select * from weather.forecast where woeid="%s" and u=\'c\'' % woeid
        f = {'q': string}
        urlendoced = urlencode(f)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' +
                          'Chrome/53.0.2785.143 Safari/537.36'
        }

        async with self.session.get(url=(url + urlendoced), headers=headers) as resp:
            if resp.status == 200:
                parsed = xmltodict.parse(await resp.text()).get('query')
                results = parsed.get('results')
                if results is None:
                    await self.bot.say("No forecast available. Try a more specific location.")
                    return
                location = 'Here it is: ' + results.get('channel').get('title')

                cover = await self.get_cover(results)
                temp = await self.get_temp(results)
                humidity = await self.get_humidity(results)
                wind = await self.get_wind(results)
                await self.bot.say(u'%s - %s, %s, %s, %s' % (location, cover, temp, humidity, wind))


def setup(bot):
    bot.add_cog(Weather(bot))
