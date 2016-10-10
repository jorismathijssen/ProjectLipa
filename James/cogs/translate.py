import json
import logging
import random

import aiohttp
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

mangle_lines = {}
errorcode = 1

log = logging.getLogger()


class Translate:
    """Cog for translating strings"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def __unload(self):
        # pray it closes
        self.bot.loop.create_task(self.session.close())

    def get_random_lang(self, long_list, short_list):
        random_index = random.randint(0, len(long_list) - 1)
        random_lang = long_list[random_index]
        if random_lang not in short_list:
            short_list.append(random_lang)
        else:
            return self.get_random_lang(long_list, short_list)
        return short_list

    async def translateMethod(self, phrase, in_lang='auto', out_lang='en'):
        url = "http://translate.googleapis.com/translate_a/single"
        headers = {
            'User-Agent': 'Mozilla/5.0' +
                          '(X11; U; Linux i686)' +
                          'Gecko/20071127 Firefox/2.0.0.11'
        }

        query = {
            "client": "gtx",
            "sl": in_lang,
            "tl": out_lang,
            "dt": "t",
            "q": phrase,
        }
        async with self.session.post(url, data=query, headers=headers) as resp:
            global errorcode
            if resp.status == 200:
                result = await resp.text()
                if result == '[,,""]':
                    return None, in_lang

                while ',,' in result:
                    result = result.replace(',,', ',null,')
                    result = result.replace('[,', '[null,')

                data = json.loads(result)

                try:
                    language = data[2]  # -2][0][0]
                except:
                    language = '?'
                errorcode = 2
                return ''.join(x[0] for x in data[0])

            elif resp.status == 404:
                errorcode = 1
                log.info('Translate Google returned status: {0}'.format(resp.status))
                return 'A 404 returned!'

            elif resp.status == 503:
                errorcode = 1
                log.info('Google returned status: {0}'.format(resp.status))
                return "A 503 returned! I spammed the google service and i cant solve the captcha ({0}). I'm sorry for the trouble!".format(
                    resp.url)

            else:
                errorcode = 1
                log.info('Translate Google returned status: {0} Response: {1} and Headers: {2}'.format(resp.status,
                                                                                                       resp.reason,
                                                                                                       resp.headers))
                return 'Is the API still working? Status: {0} Response: {1} and Headers: {2}'.format(resp.status,
                                                                                                     resp.reason,
                                                                                                     resp.headers)

    @commands.cooldown(1, 360, BucketType.user)
    @commands.command(pass_context=True, aliases=['tr'])
    async def translate(self, ctx, *, phrase=''):
        """
        Translate string after the command to English.

        (Auto Detect original language)
        """
        translation = await self.translateMethod(phrase)
        author = ctx.message.author
        if (errorcode == 2):
            await self.bot.say(author.mention + ", I have translated the text into the following: " + translation);
        if (errorcode == 1):
            await self.bot.say(author.mention + ", something went wrong. This is the message: " + translation);

    @commands.cooldown(2, 120, BucketType.user)
    @commands.command(pass_context=True, aliases=['mngl'])
    async def mangle(self, ctx, *, phrase=''):
        """
        Translate until it makes no sense.
        """

        author = ctx.message.author

        global mangle_lines
        long_lang_list = ['fr', 'de', 'es', 'it', 'no', 'he', 'la', 'ja', 'cy', 'ar', 'yi', 'zh', 'nl', 'ru', 'fi',
                          'hi', 'af', 'jw', 'mr', 'ceb', 'cs', 'ga', 'sv', 'eo', 'el', 'ms', 'lv']
        lang_list = []

        if phrase == '':
            await self.bot.say(author.mention + ", What do you want me to mangle?")
            return

        for __ in range(0, 6):
            lang_list = self.get_random_lang(long_lang_list, lang_list)
        random.shuffle(lang_list)

        for lang in lang_list:
            backup = phrase
            try:
                phrase = await self.translateMethod(phrase, 'en', lang)
            except:
                phrase = False
            if not phrase:
                phrase = backup
                break

            try:
                phrase = await self.translateMethod(phrase, lang, 'en')
            except:
                phrase = backup
                continue

            if not phrase:
                phrase = backup
                break
        if (errorcode == 1):
            await self.bot.say(author.mention + ", something went wrong. This is the message: " + phrase);
        if (errorcode == 2):
            await self.bot.say(author.mention + " mangle: " + phrase);


def setup(bot):
    bot.add_cog(Translate(bot))
