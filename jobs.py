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
import headers


class SendEmails(webapp2.RequestHandler):
	def get(self):
		emails_to_send = models.email.unsent_emails()

		logging.info(emails_to_send)

		headers.json(self.response)

		output = {
			'pending_emails': emails_to_send.count()
		}

		self.response.out.write(json.dumps(output))


app = webapp2.WSGIApplication([
	webapp2.Route(r'/jobs/email/send', handler=SendEmails),
	], debug=True)