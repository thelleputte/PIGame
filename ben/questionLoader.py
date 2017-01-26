import os
import sys
import random

class QuestionLoader:
	def __init__(self, question_file='easy1.txt', question_dir='Questions'):
		self.load_question_file(question_file=question_file, question_dir=question_dir);

	def load_question_file(self, question_file='easy1.txt', question_dir='Questions'):
		if question_dir[0] != '/':
			question_dir = os.getcwd() + '/' + question_dir
		if question_dir[-1] == '/':
			# get the full path without final '/'
			question_dir = question_dir[:-1]
		if question_file[0] == '/':
			#the input file is absolute.  don't need a question dir
			question_dir = ''

		self.question_file = question_file
		self.question_dir = question_dir
		with open(self.question_dir+'/'+self.question_file, 'r') as f:
			rawlines = f.readlines()
			self.questions = rawlines[0::2]
			self.answers = rawlines[1::2]
		print(self.questions)

	def get_question_answer(self, remove=1):
		if not len(self.questions):
			raise EmptyQuestionListException('no more questions')
		r = random.randrange(len(self.questions))
		print("r is {}".format(r) )
		(q,a) = (self.questions[r], self.answers[r])
		if remove:
			#remove by index not by value as many answers may be the same (e.g. yes or no)
			del self.questions[r]
			del self.answers[r]
		return (q,a)


class EmptyQuestionListException(Exception):
    pass

if __name__ == '__main__':
	q_file = None
	if len(sys.argv) > 1:
		q_file = str(sys.argv[1])
	if q_file:
		the_questions = QuestionLoader(question_file=q_file)
	else:
		the_questions = QuestionLoader()

	while True:
		print(the_questions.get_question_answer())