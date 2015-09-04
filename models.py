from google.appengine.ext import ndb

def read(urlsafe_key):
	return ndb.Key(urlsafe=urlsafe_key).get()

class Configuration(ndb.Model):
	key = ndb.StringProperty(required=True)
	value = ndb.StringProperty(required=True)

class Person(ndb.Model):
	name = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)

class FeedbackRequest(ndb.Model):
	requester = ndb.UserProperty(required=True)
	subject = ndb.StructuredProperty(Person)
	description = ndb.StringProperty()
	questions = ndb.StringProperty(repeated=True)

class Feedback(ndb.Model):
	question = ndb.StringProperty(required=True)
	feedback = ndb.StringProperty(required=True)

def feedback_request(requester, subject, description, questions=None):
	request = FeedbackRequest(requester=requester,
		subject=subject,
		description=description)

	if questions:
		request.questions = questions

	return request