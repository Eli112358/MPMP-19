import argparse
from sys import argv

from prime import get_primes

primes = None

"""
Verify/Confirm a given number (usually from results.json)
"""


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
