import webapp2
import jinja2
import os
import json
import logging
from urllib import quote, urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import models

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

class MainPage(webapp2.RequestHandler):
	def get(self):
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
		template = jinja_environment.get_template('request.html')
		
		people = [p for p in models.Person.query()]
		template_values = {
			'people': people,
		}

		self.response.out.write(template.render(template_values))

	def post(self):

		template = jinja_environment.get_template('request-created.html')
		
		template_values = {}

		self.response.out.write(template.render(template_values))

class Feedback(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('feedback.html')
		
		template_values = {}

		self.response.out.write(template.render(template_values))

	def post(self):

		template = jinja_environment.get_template('feedback-created.html')
		
		template_values = {}

		self.response.out.write(template.render(template_values))

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

app = webapp2.WSGIApplication([
	webapp2.Route(r'/', handler=MainPage),
	webapp2.Route(r'/dashboard', handler=Dashboard),
	webapp2.Route(r'/request', handler=RequestFeedback),
	webapp2.Route(r'/request/key', handler=Feedback),
	webapp2.Route(r'/person', handler=NewPerson),
	webapp2.Route(r'/person/<key>', handler=Person),
	], debug=True)