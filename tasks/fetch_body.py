#!/usr/bin/env python
import os
import sys
import time
from datetime import datetime
from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.api import urlfetch

from admin.functions import *
from admin.models import LiveBlogs

args = getQueryString(os.environ['QUERY_STRING'])


################################################################################
#
# Grab the data out of the database, we need this so we can see if there are any
# new blocks, or the current time, and mainly if the blog is live or not
#
################################################################################
rows = db.GqlQuery("SELECT * FROM LiveBlogs WHERE apiUrl = :1", args['apiUrl'])
if rows.count() == 0:
  print 'can\'t find row :('
  sys.exit()
  
row = rows[0]
blocks_json = simplejson.loads(row.blocks)

# we need to go and fetch the data for the story we have just been passed
#apiUrl = args['apiUrl'] + '?format=json&show-fields=body&api-key=nmkc9fw7dwmyq8xrvqnn5bkb' <--- Good API key
apiUrl = args['apiUrl'] + '?format=json&show-fields=body&api-key=gufluffykittens' # <--- Evil API key of awesomeness
result = urlfetch.fetch(url=apiUrl)

# convert the result we get back into json so we can deal with it
guardian_json = simplejson.loads(result.content)
guardian_json = guardian_json['response']['content']

# Now that we have that can we see if we can split the body up into blocks
blocks = simplejson.dumps(guardian_json['fields']['body']).replace('\/','/').split('<!-- Block ')
blocks_json = {}

for block in blocks:
  
  # If the length of the block is less than 5, then well it obviously sucks
  if len(block) < 5:
    continue
  
  # Now that we are here, lets try and extract the block number
  block_array = block.partition(' -->')
  if len(block_array) != 3:
    continue

  block_number = int(block_array[0])
  block = block_array[2]
  
  # Right, in theory we have a number, let's see if we can extract a time
  got_time = False
  
  # Try and split on the first closing <strong> we can find
  poss_time = block.partition('</strong>')
  if len(poss_time) == 3:
    block = poss_time[2].strip()
    
    poss_time = poss_time[0]
    
    # If there is a time thing, it has to happen within the first 40 chars
    # otherwise we may have a bold time somewhere in the body, but not at the
    # start, which is bad
    if len(poss_time) < 40:
      poss_time = poss_time.partition('<strong>')
      if len(poss_time) == 3:
        poss_time = poss_time[2]
        
        # now make sure we have a possible time, it needs to be 7 or more chars
        # long
        if len(poss_time) >= 7:
          
          # Try to convert it to a time
          try:
            poss_time = poss_time.replace(':','').replace('.',':')
            t = time.strptime(poss_time, '%I:%M%p')
            d = datetime(row.webPublicationDate.year, row.webPublicationDate.month, row.webPublicationDate.day, t[3], t[4])
            got_time = True
          except:
            got_time = False


  # Now that we *kinda* have the time, lets see if what have some body text
  block = block.replace('\\','')
  if len(block) >= 40:
    
    # Now put all that data into the json structure
    blocks_json[block_number] = {
      'block_number': block_number,
      'contents': block,
      'icon': ''
    }
    
    if got_time:
      blocks_json[block_number]['d'] = d.strftime('%Y-%m-%d %H:%M')
      blocks_json[block_number]['display_time'] = str(d.strftime('*%I:%M%p').replace('*0','').replace('*','')).lower()
    else:
      blocks_json[block_number]['d'] = ''
      blocks_json[block_number]['display_time'] = ''
  

row.body = simplejson.dumps(guardian_json['fields']['body'])
row.blocks = simplejson.dumps(blocks_json)
row.last_update = datetime.now()
row.fetched = 1
row.put()

print 'Content-Type: application/json; charset=UTF-8'
print ''
print simplejson.dumps(blocks_json)