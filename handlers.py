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

class RequestFeedbackOnPerson(webapp2.RequestHandler):
	def get(self, person_id):
		template = jinja_environment.get_template('feedback/create.html')

		user = users.get_current_user()
		person = models.read(person_id)

		logging.info(user)
		logging.info(person)
		
		template_values = {
			'person': person,
		}

		self.response.out.write(template.render(template_values))

	def post(self, person_id):
		user = users.get_current_user()

		description = self.request.POST.get('description')

		person = models.read(person_id)

		request = models.feedback_request(user,
			person,
			description,
			feedback.standard_questions)

		request.put()

		return webapp2.redirect('/request/' + request.key.urlsafe())
