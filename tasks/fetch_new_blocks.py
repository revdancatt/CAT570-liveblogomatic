#!/usr/bin/env python
import os
import re
import sys
import time
from random import randint
from datetime import datetime
from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.api import urlfetch

from admin.functions import *
from admin.models import LiveBlogs

args = getQueryString(os.environ['QUERY_STRING'])

def strip_html(text):
    def fixup(m):
        text = m.group(0)
        if text[:1] == "<":
            return "" # ignore tags
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        elif text[:1] == "&":
            import htmlentitydefs
            entity = htmlentitydefs.entitydefs.get(text[1:-1])
            if entity:
                if entity[:2] == "&#":
                    try:
                        return unichr(int(entity[2:-1]))
                    except ValueError:
                        pass
                else:
                    return unicode(entity, "iso-8859-1")
        return text # leave as is
    return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
    

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
blocks_json = {}

# Now we need to grab the raw blocks from the site itself
result = urlfetch.fetch(url=row.webUrl + '?refresh=true&_=' + str(randint(1,99999)) + '&_guAjaxPanel=articleBodyAjaxPanel')
body = unicode(result.content, 'utf-8')

blocks = body.split('<!-- Block ')

for block in blocks:
  
  # If the length of the block is less than 5, then well it obviously sucks
  if len(block) < 5:
    continue
  
  # Now that we are here, lets try and extract the block number
  block_array = block.partition(' -->')
  if len(block_array) != 3:
    continue

  try:
    block_number = int(block_array[0])
    block = block_array[2]
    original_block = block_array[2]
  except:
    continue

  # Right, in theory we have a number, let's see if we can extract a time
  got_time = False
  
  
  ##############################################################################
  #
  # Attempt 1!!
  #
  ##############################################################################
  
  # Try and split on the first closing <strong> we can find
  poss_time = block.partition('</strong>')
  if len(poss_time) == 3:
    block = poss_time[2].strip()
    
    poss_time = poss_time[0]
    
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
          d = datetime(row.webPublicationDate.year, row.webPublicationDate.month, row.webPublicationDate.day, t[3], t[4], 0)
          got_time = True
        except:
          got_time = False


  ##############################################################################
  #
  # Attempt 2!!
  #
  ##############################################################################

  # if we went thru all that and didn't find the time, can we see if we can
  # do it on the <time> tag instead
  if got_time == False:
    block = original_block # <--- reset the block to the state it should be in before we faffed around with it

    poss_time = block.partition('</time>')
    if len(poss_time) == 3:
      block = poss_time[2].strip()
      poss_time = poss_time[0]

      # Now we have what could potentially be the time, let's see if we can extract it
      poss_time = strip_html(poss_time)
      poss_time = poss_time.split(' ')
      poss_time = poss_time[len(poss_time)-1].strip()
      
      # now make sure we have a possible time, it needs to be 7 or more chars
      # long
      if len(poss_time) >= 7:
        
        # Try to convert it to a time
        try:
          poss_time = poss_time.replace(':','').replace('.',':')
          t = time.strptime(poss_time, '%I:%M%p')
          d = datetime(row.webPublicationDate.year, row.webPublicationDate.month, row.webPublicationDate.day, t[3], t[4], 0)
          got_time = True
        except:
          got_time = False

  if got_time == False:
    d = datetime.now()
    d = datetime(d.year, d.month, d.day, d.hour, d.minute, 0)
    got_time = True
    

  # Now that we *kinda* have the time, lets see if what have some body text
  # block = block.replace('\r', '').replace('\n', '').replace('\t', '')
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

#row.blocks = simplejson.dumps(blocks_json)
row.body = body
row.blocks = simplejson.dumps(blocks_json)
row.last_update = datetime.now()
row.fetched = 1
row.put()

print 'Content-Type: application/json; charset=UTF-8'
print ''
print simplejson.dumps(blocks_json)