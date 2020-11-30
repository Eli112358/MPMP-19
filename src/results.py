import json

from main import data_path

"""
Display results so far,
Namely, how far it's searched, and the largest match
"""


class FormattedNumber:

	def __init__(self, n):
		self.n = n
		self.width = None

	def __len__(self):
		return len(self.commas)

	def __str__(self):
		return self.commas.rjust(self.width)

	@property
	def commas(self):
		return f'{self.n:,}'

	def set_widths(self, other):
		self.width = other.width = max(len(self), len(other))


if __name__ == '__main__':
	data = json.load(open(data_path / 'results.json'))
	last = FormattedNumber(data['last_checked'])
	largest = FormattedNumber(data['results'][-1])
	last.set_widths(largest)
	print(f'{str(last)} : Search space')
	print(f'{str(largest)} : Largest match')
