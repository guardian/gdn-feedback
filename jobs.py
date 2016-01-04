import webapp2
import jinja2
import os
import json
import logging
from urllib import quote, urlencode

from google.appengine.api import urlfetch, users
from google.appengine.ext import ndb
from google.appengine.api import mail

import models
import feedback
import handlers
import headers
import configuration

class SendEmails(webapp2.RequestHandler):
	def get(self):
		emails_to_send = models.email.unsent_emails()

		logging.info(emails_to_send)

		sender_address = configuration.lookup('EMAIL_FROM')

		for email in emails_to_send:
			mail.send_mail(sender_address, email.to, email.subject, email.message)
			logging.info(email)
			email.sent = True
			email.put()

		headers.json(self.response)

		output = {
			'pending_emails': emails_to_send.count()
		}

		self.response.out.write(json.dumps(output))


app = webapp2.WSGIApplication([
	webapp2.Route(r'/jobs/email/send', handler=SendEmails),
	], debug=True)