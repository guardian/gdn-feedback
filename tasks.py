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

class EmailFeedbackInvitation(webapp2.RequestHandler):
	def post(self):
		send_to = self.request.get('to')
		message = self.request.get('message')

		logging.info(send_to)
		logging.info(message)

		email = models.email.Message(to=send_to, message=message)

		self.response.out.write("Hello world")


app = webapp2.WSGIApplication([
	webapp2.Route(r'/tasks/email/feedback/invite', handler=EmailFeedbackInvitation),
	], debug=True)