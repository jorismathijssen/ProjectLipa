import aiohttp
import json
import logging
import random
from discord.ext import commands

mangle_lines = {}

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
            "q" : phrase,
        }
        async with self.session.post(url, data=query, headers=headers) as resp:
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

                return ''.join(x[0] for x in data[0])

            elif resp.status == 404:
                return await 'A 404 returned, is translation API up?'
                log.info('Translate Google returned status: {0}'.format(resp.status))
            else:
                return await 'Something happend, is the API still working?'
                log.info('Translate Google returned status: {0} Response: {1} and Headers: {2}'.format(resp.status,
                                                                                                       resp.reason,
                                                                                                       resp.headers))

    @commands.command(pass_context=True, aliases=['tr'])
    async def translate(self,ctx, *, phrase=''):
        """
        Translate string after the command to English.

        (Auto Detect original language)
        """
        translation = await self.translateMethod(phrase)
        author = ctx.message.author
        await self.bot.say(author.mention + ", I have translated the text into the following: " + translation);

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
        await self.bot.say(author.mention + ", I have mangled the text into the following: " + phrase);

def setup(bot):
    bot.add_cog(Translate(bot))