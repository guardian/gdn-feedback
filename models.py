import logging

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
	subject = ndb.KeyProperty(Person)
	description = ndb.StringProperty()
	questions = ndb.StringProperty(repeated=True)
	active = ndb.BooleanProperty(default=True)
	due_date = ndb.DateProperty()
	invited = ndb.StringProperty(repeated=True)

class Feedback(ndb.Model):
	provider = ndb.UserProperty(required=True)
	request = ndb.KeyProperty(FeedbackRequest, required=True)
	question = ndb.StringProperty(required=True)
	feedback = ndb.StringProperty(required=True)

def feedback_request(requester, subject, description, questions=None, due_date=None):
	request = FeedbackRequest(requester=requester,
		subject=subject.key,
		description=description)

	if questions:
		request.questions = questions

	if due_date:
		request.due_date = due_date

	return request

def feedback(provider, request, question, feedback):
	current_feedback = Feedback.query(Feedback.provider == provider, Feedback.request == request.key, Feedback.question == question).get()

	if not current_feedback:
		current_feedback = Feedback(provider = provider,
			request = request.key,
			question = question,
			feedback = feedback)

	return current_feedback

def current_feedback(provider, request):
	feedback = {}

	for q in request.questions:
		#logging.info(q)
		current_feedback = Feedback.query().filter(Feedback.provider == provider).filter(Feedback.request == request.key).filter(Feedback.question == q).get()
		if current_feedback:
			feedback[q] = current_feedback.feedback

	return feedback

def everyone():
	return Person.query().order(Person.name)

def requests(user):
	return FeedbackRequest.query().filter(FeedbackRequest.requester == user).filter(FeedbackRequest.active == True).order(FeedbackRequest.description)

def all_feedback(request):
	return Feedback.query().filter(Feedback.request == request.key)

def active_feedback(request):
	return Feedback.query().filter(Feedback.request == request.key)

def respondents_count(request):
	return len({feedback.provider for feedback in Feedback.query(Feedback.request == request.key)})

def outstanding_requests(user):
	return FeedbackRequest.query().filter(FeedbackRequest.active == True)\
		.filter(FeedbackRequest.invited == user.email())

def delete_request(request_id):
	request = read(request_id)
	if respondents_count(request) < 1:
		request.key.delete()
	return request

def status(user, request_id, status):
	request = read(request_id)
	request.active = status
	request.put()

	return request