
formats = {
	'Start - Continue - Stop',
	'Impact',
}

standard_questions = [
	'What should they keep doing?',
	'What should they stop doing?',
	'What should they start doing?'
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