#!/usr/bin/env python
from google.appengine.api import urlfetch
import sys


readability = {}

# Woot, so the first thing we need to do is actually go fetch the document
def fetchDoc(webUrl):
	
	result = urlfetch.fetch(url=webUrl)
	if result.status_code != 200:
		return ''

	return result.content
	
def main():
	
	# Go and grab the webpage to see what we can do with it
	webUrl = 'http://www.guardian.co.uk/world/2011/jan/10/gabrielle-giffords-us-politics'
	content = fetchDoc(webUrl)
	
	if content == '':
		print ''
		print 'could\'t fetch file'
		sys.exit()
		
	#	Ok it seems that we got it, what next?
	print ''
	print content

if __name__ == '__main__':
	main()