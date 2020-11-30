import argparse
import dbm
import json
import os
import pathlib
from multiprocessing import Process, Value
from sys import argv

import keyboard

data = dict(
	last_checked=0,
	results=[],
	running_total=0,
)
data_path = pathlib.Path('../data')
db = None
iter_range = Value('i', -1)
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


def check():

	def n():
		return data['last_checked']

	prime = next(primes)
	p = prime[1]
	data['running_total'] += p ** 2
	if data['running_total'] % n() == 0:
		data['results'].append(n())
		print(n())
	data['last_checked'] += 1
	if n() % args.interval == 0:
		save('Auto-save')


def running():
	condition = iter_range.value != 0
	if iter_range.value > 0:
		iter_range.value -= 1
	return condition


def key_handler(_range):
	keyboard.wait('esc')
	_range.value = 0


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Search for all values of N, where the sum of the '
		            'squares of the first N primes is a multiple of N. '
		            '(MPMP19)',
		epilog='You can use Esc at any point after "Done; running" to '
		       'stop computation, save and exit'
	)
	parser.add_argument('-r', dest='range', metavar='R', type=int, default=-1,
	                    help='Iteration range before exiting '
	                         '(will compute N to (N + R), N is where it left off; '
	                         'default of -1 will run indefinitely and requires Esc to save & exit)')
	parser.add_argument('-as', dest='interval', metavar='S', type=int, default=100,
	                    help='Auto-save when N is a multiple of S (no commas; default 100)')
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
	iter_range.value = args.range
	process = Process(target=key_handler, args=(iter_range,))
	process.start()
	while running():
		check()
	save('Quit', True)
