import webapp2
import jinja2
import os
import json
import logging
from urllib import quote, urlencode

from google.appengine.api import urlfetch, users
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

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

		responses = models.active_feedback(request)
		
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

			for email in emails:
				payload = {
					'to': email,
					'feedback_request': feedback_request,
				}

				taskqueue.add(url='/tasks/email/feedback/invite',
					queue_name='email',
					params=payload)


		feedback_request.invited.extend(emails)
		feedback_request.put()

		return webapp2.redirect('/request/' + request_id)


class Feedback(webapp2.RequestHandler):
	def get(self, request_id):
		template = jinja_environment.get_template('feedback.html')

		user = users.get_current_user()

		template_values = {
			'feedback': {},
			'show_summary': False,
			'saved': False,
			'show_delete': False,
		}


		request = models.read(request_id)


		template_values['request'] = request
		template_values['feedback'] = models.current_feedback(user, request)

		if request.requester == user:
			template_values['show_summary'] = True

		status = self.request.get('status')

		if status == 'saved':
			template_values['saved'] = True

		if models.respondents_count(request) < 1:
			template_values['show_delete'] = True

		self.response.out.write(template.render(template_values))

	def post(self, request_id):
		user = users.get_current_user()
		request = models.read(request_id)

		for q in request.questions:
			feedback = self.request.POST.get(q)
			if not feedback:
				continue

			saved_feedback = models.feedback(user, request, q, feedback)

			saved_feedback.feedback = feedback
			saved_feedback.put()

		return webapp2.redirect('/request/{0}?status=saved'.format(request_id))

class DeleteFeedback(webapp2.RequestHandler):

	def post(self, request_id):
		user = users.get_current_user()
		request = models.delete_request(request_id)

		return webapp2.redirect('/dashboard')

class FeedbackStatus(webapp2.RequestHandler):

	def post(self, request_id):
		user = users.get_current_user()

		status_label = self.request.get('status', 'active')
		logging.info(status_label)

		status = True if status_label == 'active' else False
		request = models.status(user, request_id, status)

		return webapp2.redirect('/request/{0}'.format(request_id))