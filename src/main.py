import argparse
import dbm
import json
import os
import pathlib
from sys import argv

data = dict(
	last_checked=0,
	results=[],
	running_total=0,
)
data_path = pathlib.Path('../data')
db = None
primes = None


def get_primes():
	"""
	Sieve of Eratosthenes
	From https://stackoverflow.com/a/568618/2640292

	This implementation, however, reads and stores its variables to disk via dbm
	This is so we can resume the computation where it left off, every time this script is ran

	I initially tried using pickle, however, the file size quickly grew to the limit of what pickle can handle
	"""

	def i():
		try:
			return int(db['i'])
		except KeyError:
			db['i'] = str(0)
			return i()

	def q():
		try:
			return int(db['q'])
		except KeyError:
			db['q'] = str(2)
			return q()

	def setdefault(key, default):
		if key not in db:
			db[key] = json.dumps(default)

	def append(key, value):
		_list = json.loads(db[key])
		_list.append(value)
		db[key] = json.dumps(_list)

	i()
	q()
	while True:
		if db['q'] not in db:
			yield i(), q()
			db['i'] = str(i() + 1)
			db[str(q() ** 2)] = json.dumps([q()])
		else:
			for n in json.loads(db[db['q']]):
				n_q = str(n + q())
				setdefault(n_q, [])
				append(n_q, n)
			del db[db['q']]
		db['q'] = str(q() + 1)


def save(name, close=False):
	print(f'[{name}] Saving ...')
	json.dump(data, open(data_path / 'results.json', 'w'), indent='\t')
	if close:
		db.close()
	print(f'[{name}] Done')


def check(n):
	prime = next(primes)
	p = prime[1]
	data['running_total'] += p ** 2
	data['last_checked'] = n
	if data['running_total'] % n == 0:
		data['results'].append(n)
		print(n)
	if n % args.interval == 0:
		save('Auto-save')


def running():
	condition = args.range != 0
	if args.range > 0:
		args.range -= 1
	return condition


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Search for all values of N, where the sum of the '
		            'squares of the first N primes is a multiple of N. '
		            '(MPMP19)',
		epilog='You can use Ctrl+C at any point after "Done; running" to '
		       'stop computation, save and exit'
	)
	parser.add_argument('-r', dest='range', metavar='R', type=int, default=-1,
	                    help='Iteration range before exiting '
	                         '(will compute N to (N + R), N is where it left off; '
	                         'default of -1 will run indefinitely and requires Ctrl+C to save & exit)')
	parser.add_argument('-as', dest='interval', metavar='S', type=int, default=1000,
	                    help='Auto-save when N is a multiple of S (no commas; default 1000)')
	args = parser.parse_args(argv[1:])
	print('Loading...')
	try:
		if not os.path.isdir(data_path):
			os.makedirs(data_path)
		data = json.load(open(data_path / 'results.json'))
	except FileNotFoundError:
		save('Setup')
	db = dbm.open(str(data_path / 'generator.db'), 'c')
	print('Done; running')
	primes = get_primes()
	while running():
		try:
			check(data['last_checked'] + 1)
		except KeyboardInterrupt:
			args.range = 0
	save('Quit', True)
