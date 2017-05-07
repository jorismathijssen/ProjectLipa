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
def fuckyou():
        return "```What the fuck did you just fucking say about me, you little bitch? I'll have you know I graduated top of my class in the Navy Seals, and I've been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare and I'm the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA and your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing you call your life. You're fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that's just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit. If only you could have known what unholy retribution your little \"clever\" comment was about to bring down upon you, maybe you would have held your fucking tongue. But you couldn't, you didn't, and now you're paying the price, you goddamn idiot. I will shit fury all over you and you will drown in it. You're fucking dead, kiddo.```"
