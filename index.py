#!/usr/bin/env python
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from datetime import datetime, timedelta
from google.appengine.ext import webapp
from admin.models import LiveBlogs
from google.appengine.ext import db
from django.utils import simplejson
import sys
import os

class Main(webapp.RequestHandler):
  def get(self):


    # Get the most recent liveblogs
    rows = db.GqlQuery("SELECT * FROM LiveBlogs WHERE isLive = 1 AND fetched = 1 ORDER BY webPublicationDate DESC")
    
    liveBlogs = []
    for row in rows:
      liveBlog = {'webTitle': row.webTitle, 'sectionId': row.sectionId, 'sectionName': row.sectionName, 'apiUrl': row.apiUrl.replace('http://content.guardianapis.com/','')}
      liveBlogs.append(liveBlog)

    
    # Get the most recent liveblogs
    rows = db.GqlQuery("SELECT * FROM LiveBlogs WHERE isLive = 0 AND fetched = 1 ORDER BY webPublicationDate DESC")
    
    deadBlogs = []
    for row in rows:
      deadBlog = {'webTitle': row.webTitle, 'sectionId': row.sectionId, 'sectionName': row.sectionName, 'apiUrl': row.apiUrl.replace('http://content.guardianapis.com/','')}
      deadBlogs.append(deadBlog)

    
    
    template_values = {
      'msg': 'hello world',
      'liveBlogs': liveBlogs,
      'deadBlogs': deadBlogs,
      'thingy': os.environ['HTTP_USER_AGENT'],
    }
    
    template_values['DEBUG'] = os.environ['SERVER_SOFTWARE'].startswith('Dev');

    # Just fall back to the top level groups page
    if 'iPad' in os.environ['HTTP_USER_AGENT']:
      path = os.path.join(os.path.dirname(__file__), 'templates/index_ipad.html')
    else:
      path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, template_values))


# I have no idea what's going on here, but I seem to need to 
# match up the path bit here with what brought us here from the
# main.py file
application = webapp.WSGIApplication(
                                     [('/.*', Main)],
                                     debug=True)
    
def main():
  run_wsgi_app(application)

  
if __name__ == "__main__":
  main()
  
  
  
  
