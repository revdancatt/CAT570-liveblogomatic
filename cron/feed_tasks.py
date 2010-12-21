#!/usr/bin/env python
from google.appengine.ext import db
from google.appengine.api.labs import taskqueue
from admin.models import LiveBlogs


################################################################################
#
# Grab all the records that haven't been fetched yet
#
################################################################################

rows = db.GqlQuery("SELECT * FROM LiveBlogs WHERE fetched = 1 AND isLive = 1")

counter = 1
for row in rows:
  print row.apiUrl
  taskqueue.add(method='GET', url='/tasks/fetch_new_blocks?apiUrl=' + row.apiUrl, countdown=counter)
  taskqueue.add(method='GET', url='/tasks/fetch_new_blocks?apiUrl=' + row.apiUrl, countdown=counter+30)
  counter+=1

################################################################################
#
# Grab all the records that haven't been fetched yet
#
################################################################################

rows = db.GqlQuery("SELECT * FROM LiveBlogs WHERE fetched = 0")
print ''

for row in rows:
  print row.apiUrl
  taskqueue.add(method='GET', url='/tasks/fetch_new_blocks?apiUrl=' + row.apiUrl, countdown=counter)
  taskqueue.add(method='GET', url='/tasks/fetch_new_blocks?apiUrl=' + row.apiUrl, countdown=counter+30)
  counter+=1


