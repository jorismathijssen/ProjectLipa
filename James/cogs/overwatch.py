"""
overwatch.py - Ask the overwatch wikia a question
Copyright 2016, Guus Beckett reupload.nl
Licensed under the GPL 2.

"""
import wikia

# title_tag_data = re.compile('<(/?)title( [^>]+)?>', re.IGNORECASE)
# r =requests.get('http://overwatch.wikia.com/wiki/Ana')
def searchOverwatchWikia(searchQuery):
	try:
		summary = wikia.summary("Overwatch", searchQuery)
		if("REDIRECT" in summary):
			summary = wikia.summary("Overwatch", summary.replace("REDIRECT",""))
		return summary
	except:
		return "Sorry, die kon ik niet vinden :("
		
def giveOverwatchWikiaURL(searchQuery):
	try:
		page = wikia.page("Overwatch",searchQuery)
		return page.url
	except:
		return "Sorry, die kon ik niet vinden :("