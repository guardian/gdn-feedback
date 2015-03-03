import webapp2
import jinja2
import os
import json
import logging
from urllib import quote, urlencode

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from models import Person

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
		
		template_values = {}

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

		person = Person.query(Person.email == email).get()

		if not person:
			person = Person(name=name, email=email)
			person.put()

		return webapp2.redirect('/person/' + person.key.urlsafe())

app = webapp2.WSGIApplication([
	webapp2.Route(r'/', handler=MainPage),
	webapp2.Route(r'/dashboard', handler=Dashboard),
	webapp2.Route(r'/request', handler=RequestFeedback),
	webapp2.Route(r'/request/key', handler=Feedback),
	webapp2.Route(r'/person', handler=NewPerson),
	], debug=True)