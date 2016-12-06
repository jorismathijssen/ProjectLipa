"""
8ball.py - Ask the magic 8ball a question
Copyright 2013, Sander Brand http://brantje.com
Licensed under the Eiffel Forum License 2.
Ported to James by Guus Beckett 2016
http://sopel.dfbta.net
"""
import asyncio
import random
def eightball():
		messages = ["Het is zeker","Het is beslist zo","Zonder twijfel","Ja, zeker weten!","Je kan er op vertrouwen","Zover ik kan zien, ja","Hoogstwaarschijnlijk","Nee","Het vooruitzicht is goed","Tekenen wijzen op ja","Reken er maar niet op","Mijn reactie is nee","God zegt nee","Erg twijfelachtig","Het vooruitzicht is niet goed"]
		answer = random.randint(0,len(messages)-1)
		return messages[answer]
async def laugh():
		respond = ['xDDDDD', 'XD', 'XDDDD', 'haha','2funny']
		randtime = random.uniform(0, 3)
		await asyncio.sleep(randtime)
		return random.choice(respond)
async def haha():
		respond = ['haha', 'lol', 'rofl', 'hm', 'hmmmm...','2funny']
		randtime = random.uniform(0, 3)
		await asyncio.sleep(randtime)
		return random.choice(respond)
def bye():
	return random.choice(('Dag', 'Goodbye', 'Seeya', 'Auf Wiedersehen', 'Au revoir', 'Ttyl', 'Later', 'Houdoe', 'Dag!', 'Doei!'))
def thanks():
	return random.choice(('Geen probleem', 'Graag gedaan', 'Geen dank'))