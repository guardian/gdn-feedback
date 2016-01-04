import logging

from google.appengine.ext import ndb

class Message(ndb.Model):
	sent = ndb.BooleanProperty(default=False)
	to = ndb.StringProperty(required=True)
	subject = ndb.StringProperty(required=True)
	message = ndb.TextProperty(required=True)

def unsent_emails():
	return Message.query().filter(Message.sent == False)