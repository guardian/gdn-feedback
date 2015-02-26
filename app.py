import webapp2
import jinja2
import os
import json
import logging
from urllib import quote, urlencode
from google.appengine.api import urlfetch

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


app = webapp2.WSGIApplication([
	webapp2.Route(r'/', handler=MainPage),
	webapp2.Route(r'/dashboard', handler=Dashboard),
	webapp2.Route(r'/request', handler=RequestFeedback),
	], debug=True)