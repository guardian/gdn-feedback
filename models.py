from google.appengine.ext import ndb

class Configuration(ndb.Model):
	key = ndb.StringProperty(required=True)
	value = ndb.StringProperty(required=True)

class Person(ndb.Model):
	name = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)