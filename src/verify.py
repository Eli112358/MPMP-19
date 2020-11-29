import argparse
from sys import argv

primes = None

"""
Verify/Confirm a given number (usually from results.json)
"""


def get_primes():
	"""
	Sieve of Eratosthenes
	From https://stackoverflow.com/a/568618/2640292
	"""
	d = {}
	q = 2
	while True:
		if q not in d:
			yield q
			d[q * q] = [q]
		else:
			for n in d[q]:
				d.setdefault(n + q, []).append(n)
			del d[q]
		q += 1


def check(n):
	global primes
	total = sum([next(primes) ** 2 for _ in range(n)])
	print(n, total % n == 0)


if __name__ == '__main__':
	primes = get_primes()
	parser = argparse.ArgumentParser(description='Verify a number (from results)')
	parser.add_argument('n', metavar='N', type=int, default=19,
	                    help='Number to verify')
	args = parser.parse_args(argv[1:])
	check(args.n)
