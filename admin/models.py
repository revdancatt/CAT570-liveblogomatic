#!/usr/bin/env python
from google.appengine.ext import db

class LiveBlogs(db.Model):

  sectionName             = db.StringProperty(default='')
  sectionId               = db.StringProperty(default='')
  webUrl                  = db.StringProperty(default='')
  apiUrl                  = db.StringProperty(default='')
  thumbnail               = db.StringProperty(default='')
  webTitle                = db.TextProperty(default='')
  body                    = db.TextProperty(default='')
  blocks                  = db.TextProperty(default='')
  isLive                  = db.IntegerProperty(default=0)
  liveBloggingNow         = db.IntegerProperty(default=0)
  fetched                 = db.IntegerProperty(default=0)
  backfilled              = db.IntegerProperty(default=0)
  webPublicationDate      = db.DateTimeProperty()
  first_update            = db.DateTimeProperty(auto_now_add=True, required=True)
  last_update             = db.DateTimeProperty(auto_now_add=True, required=True)