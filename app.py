import webapp2
import jinja2
import os
import json
import logging
from urllib import quote, urlencode

from google.appengine.api import urlfetch, users
from google.appengine.ext import ndb

import models
import feedback
import handlers

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

class MainPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()

		if user:
			return webapp2.redirect('/dashboard')

		template = jinja_environment.get_template('index.html')
		
		template_values = {}

		self.response.out.write(template.render(template_values))

class Dashboard(webapp2.RequestHandler):
	def get(self):

		template = jinja_environment.get_template('dashboard.html')
		
		template_values = {}

		self.response.out.write(template.render(template_values))

class RequestFeedback(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('feedback/request.html')
		
		people = [p for p in models.everyone()]
		template_values = {
			'people': people,
			'formats': feedback.formats,
		}

		self.response.out.write(template.render(template_values))

	def post(self):
		user = users.get_current_user()

		person_id = self.request.POST.get('person_key')

		description = self.request.POST.get('description')

		person = models.read(person_id)

		request = models.feedback_request(user,
			person,
			description,
			feedback.standard_questions)

		request.put()

		return webapp2.redirect('/request/' + request.key.urlsafe())

class NewPerson(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('person/new.html')
		
		template_values = {}

		self.response.out.write(template.render(template_values))

	def post(self):

		name = self.request.get('name')
		email = self.request.get('email')

		person = models.Person.query(models.Person.email == email).get()

		if not person:
			person = models.Person(name=name, email=email)
			person.put()

		return webapp2.redirect('/person/' + person.key.urlsafe())

class Person(webapp2.RequestHandler):
	def get(self, key):
		template = jinja_environment.get_template('person/index.html')
		
		template_values = {
			'person': ndb.Key(urlsafe=key).get(),
		}

		self.response.out.write(template.render(template_values))

class People(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('person/list.html')
		
		template_values = {
			'people': models.everyone()
		}

		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
	webapp2.Route(r'/', handler=MainPage),
	webapp2.Route(r'/dashboard', handler=Dashboard),
	webapp2.Route(r'/request', handler=RequestFeedback),
	webapp2.Route(r'/request/<request_id>', handler=handlers.Feedback),
	webapp2.Route(r'/request/<request_id>/summary', handler=handlers.FeedbackSummary),
	webapp2.Route(r'/request/<request_id>/summary/text', handler=handlers.FeedbackSummaryText),
	webapp2.Route(r'/request/<request_id>/delete', handler=handlers.DeleteFeedback),
	webapp2.Route(r'/request/<request_id>/status', handler=handlers.FeedbackStatus),
	webapp2.Route(r'/people', handler=People),
	webapp2.Route(r'/person', handler=NewPerson),
	webapp2.Route(r'/person/<key>', handler=Person),
	webapp2.Route(r'/person/<person_id>/request', handler=handlers.RequestFeedbackOnPerson),
	webapp2.Route(r'/requests', handler=handlers.YourRequests),
	webapp2.Route(r'/feedback/outstanding', handler=handlers.FeedbackInvitations),
	webapp2.Route(r'/feedback/invitation/<request_id>', handler=handlers.FeedbackInvitation),
	], debug=True)