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

    apiUrl = '**' + os.environ['PATH_INFO']
    apiUrl = apiUrl.replace('**/view/', 'http://content.guardianapis.com/')

    rows = db.GqlQuery("SELECT * FROM LiveBlogs WHERE apiUrl = :1", apiUrl)
    
    blocks = []
    blocks_json = simplejson.loads(rows[0].blocks)

    max_value = 0
    for block in blocks_json:
      if int(block) > max_value:
        max_value = int(block)
    
    blocks = [[]*max_value for x in xrange(max_value)]

    for block in blocks_json:
      blocks_json[block]['contents'] = blocks_json[block]['contents'].replace('u00','\u00')
      blocks[int(block)-1] = blocks_json[block]
    
    
    template_values = {
      'liveBlog': rows[0],
      'blocks_json': simplejson.dumps(blocks),
      'current_block': max_value,
      'apiUrl': apiUrl,
      'agent': os.environ['HTTP_USER_AGENT'],
    }
    
    template_values['DEBUG'] = os.environ['SERVER_SOFTWARE'].startswith('Dev');

    # Just fall back to the top level groups page
    if 'iPad' in os.environ['HTTP_USER_AGENT']:
      path = os.path.join(os.path.dirname(__file__), 'templates/view_ipad.html')
    else:
      path = os.path.join(os.path.dirname(__file__), 'templates/view.html')
    self.response.out.write(template.render(path, template_values))


# I have no idea what's going on here, but I seem to need to 
# match up the path bit here with what brought us here from the
# main.py file
application = webapp.WSGIApplication(
                                     [('/view/.*', Main)],
                                     debug=True)
    
def main():
  run_wsgi_app(application)

  
if __name__ == "__main__":
  main()
  
  
  
  
