#!/usr/bin/env python
from google.appengine.api.labs import taskqueue
from google.appengine.api import urlfetch
from google.appengine.ext import db
from django.utils import simplejson
from admin.models import LiveBlogs

from datetime import datetime

import logging
import time
import sys

################################################################################
#
# Go get the latest headlines from the guardian API, keyless
#
################################################################################

fetch_url = 'http://content.guardianapis.com/search?tag=tone%2Fminutebyminute%2C-sport%2Fsport&section=-sport,-football&order-by=newest&format=json&show-fields=headline%2Cthumbnail%2CliveBloggingNow&api-key=nmkc9fw7dwmyq8xrvqnn5bkb'
result = urlfetch.fetch(url=fetch_url)

#
# If something went wrong, bail out
#
if result.status_code != 200:
  sys.exit()


#
# See if we can convert to json
#
try:
  json = simplejson.loads(result.content)
  json = json['response']['results']
except Exception:
  sys.exit()

# Now we need to go thru each one and check to see if we already have the record
blocks_json = {}
print ''
foundNew = False

for liveblog in json:

  try:
    # Make a note of if it's liveBlogging or not
    liveBloggingNow = 0
    isLive = 0
    if liveblog['fields']['liveBloggingNow'] == 'true':
      liveBloggingNow = 1
      isLive = 1
  
    # I want to do the date dance first, as that's the most complex bit
    webPublicationDate = liveblog['webPublicationDate'].replace('Z','')
    pd = datetime.strptime(webPublicationDate.split('+')[0], '%Y-%m-%dT%H:%M:%S')    
    nd = datetime.now()
    diff = int(time.mktime(nd.timetuple())) - int(time.mktime(pd.timetuple()))
    diff = diff / 60 / 60 # 60 seconds per minute, 60 minutes per hour
  
    if diff > 24:
      isLive = 0
    else:
      isLive = 1
      
    # Now that we have done that we need to see if we have to add the row
    rows = db.GqlQuery("SELECT * FROM LiveBlogs WHERE apiUrl = :1", liveblog['apiUrl'])
    if rows.count() == 0:
  
      print 'New: ' + liveblog['webUrl']
      foundNew = True
      
      row = LiveBlogs()
      row.sectionName         = liveblog['sectionName']
      row.sectionId           = liveblog['sectionId']
      row.webUrl              = liveblog['webUrl']
      row.apiUrl              = liveblog['apiUrl']
      
      if 'thumbnail' in liveblog['fields'] and liveblog['fields']['thumbnail'] != '':
        row.thumbnail         = liveblog['fields']['thumbnail']
        
      row.webTitle            = liveblog['webTitle']
      row.isLive              = isLive
      row.liveBloggingNow     = liveBloggingNow
      row.webPublicationDate  = pd
      row.last_update         = datetime.now()
      row.blocks              = simplejson.dumps(blocks_json)
      row.put()
    else:
      
      # If we are live blogging then we want to update the time
      if isLive == 1:
        row = rows[0]
        row.last_update = datetime.now()
        row.put()
      else:
        # if we are no longer blogging, but the last time we check we
        # were then update the record
        row = rows[0]
        if row.isLive == 1:
          row.isLive = 0
          row.last_update = datetime.now()
          row.put()
  except:
    print ''
    print 'hummm, something didn\'t work'
    print sys.exc_info()[1]
    

if foundNew == True:
  taskqueue.add(url='/tasks/do_twitter_dance', countdown=5)

print ''
print 'done' # just to prove we got here o_O
