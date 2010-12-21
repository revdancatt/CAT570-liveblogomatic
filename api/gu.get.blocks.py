#!/usr/bin/env python
from google.appengine.api import memcache
from datetime import datetime, timedelta
from admin.models import LiveBlogs
from google.appengine.ext import db
from django.utils import simplejson
import sys
import os

apiUrl = os.environ['PATH_INFO']
apiUrl = apiUrl.replace('/api/gu.get.blocks/', 'http://content.guardianapis.com/')

apiUrl = apiUrl.split('/')

block_number = int(apiUrl.pop())
apiUrl = '/'.join(apiUrl)

rows = db.GqlQuery("SELECT * FROM LiveBlogs WHERE apiUrl = :1", apiUrl)

blocks = []
blocks_json = simplejson.loads(rows[0].blocks)

max_block = 0
for block in blocks_json:
  if int(block) > max_block:
    max_block = int(block)
    
new_blocks_json = {}
for n in range(block_number+1, max_block+1):
  new_blocks_json[int(n)] = blocks_json[str(n)]

print 'Cache-Control: public,max-age=30'
print 'Content-Type: application/json; charset=UTF-8'
print ''
print simplejson.dumps(new_blocks_json)