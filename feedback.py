
formats = {
	'Start - Continue - Stop',
	'Impact',
}

standard_questions = [
	'What have they done well?',
	'What should they try doing or do more of?',
	'What do need from the organisation, management or other team members?',
]

def summarise_feedback(responses):

	def group_responses(acc, response):
		question = response.question
		if question in acc:
			acc[question].append(response.feedback)
		else:
			acc[question] = [response.feedback]

		return acc

	return reduce(group_responses, responses, {})