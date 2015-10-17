import webapp2
import jinja2
import os
import json
import logging
from urllib import quote, urlencode

from google.appengine.api import urlfetch, users
from google.appengine.ext import ndb

import isodate

import models
import feedback
import handlers
import headers

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

class RequestFeedbackOnPerson(webapp2.RequestHandler):
	def get(self, person_id):
		template = jinja_environment.get_template('feedback/create.html')

		user = users.get_current_user()
		person = models.read(person_id)
		
		template_values = {
			'person': person,
		}

		self.response.out.write(template.render(template_values))

	def post(self, person_id):
		user = users.get_current_user()

		description = self.request.POST.get('description')
		due_date = self.request.POST.get('due_date')

		if due_date:
			due_date = isodate.parse_date(due_date)

		person = models.read(person_id)

		request = models.feedback_request(user,
			person,
			description,
			feedback.standard_questions,
			due_date)

		request.put()

		return webapp2.redirect('/request/' + request.key.urlsafe())

class YourRequests(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()

		template = jinja_environment.get_template('request/list.html')

		def decorate_feedback_requests(request):
			request.respondent_count = models.respondents_count(request)
			return request
		
		outstanding_requests = map(decorate_feedback_requests, models.requests(user))

		template_values = {
			'requests': outstanding_requests
		}

		self.response.out.write(template.render(template_values))

class FeedbackSummary(webapp2.RequestHandler):
	def get(self, request_id):
		user = users.get_current_user()
		request = models.read(request_id)

		if request.requester != user:
			return webapp2.redirect('/dashboard')

		template = jinja_environment.get_template('feedback/summary.html')

		responses = models.all_feedback(request)
		
		template_values = {
			'request': request,
			'responses': responses,
			'respondees': {r.provider for r in responses},
			'summary': feedback.summarise_feedback(responses),
		}

		self.response.out.write(template.render(template_values))

class FeedbackSummaryText(webapp2.RequestHandler):
	def get(self, request_id):
		user = users.get_current_user()
		request = models.read(request_id)

		if request.requester != user:
			return webapp2.redirect('/dashboard')

		template = jinja_environment.get_template('feedback/summary.txt')

		responses = models.all_feedback(request)
		
		template_values = {
			'summary': feedback.summarise_feedback(responses),
		}

		headers.text(self.response)

		self.response.out.write(template.render(template_values))


class FeedbackInvitations(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		feedback_requests = models.outstanding_requests(user)

		template = jinja_environment.get_template('feedback/outstanding.html')

		template_values = {
			'feedback_requests': feedback_requests,
		}

		self.response.out.write(template.render(template_values))

class FeedbackInvitation(webapp2.RequestHandler):
	def post(self, request_id):
		user = users.get_current_user()

		feedback_request = models.read(request_id)

		emails = self.request.POST.get('emails')

		if emails:
			emails = emails.split(",")
			emails = map(lambda s: s.strip(), emails)

		feedback_request.invited.extend(emails)
		feedback_request.put()

		return webapp2.redirect('/request/' + request_id)

		