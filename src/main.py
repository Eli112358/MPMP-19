import argparse
import dbm
import json
import os
import pathlib
from multiprocessing import Process, Value
from sys import argv

import keyboard

from prime import get_primes_dbm

data = dict(
	last_checked=0,
	results=[],
	running_total=0,
)
data_path = pathlib.Path('../data')
db = None
iter_range = Value('i', -1)
primes = None


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
		epilog='You can use Esc at any point after "Running..." to '
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
	primes = get_primes_dbm(db)
	iter_range.value = args.range
	process = Process(target=key_handler, args=(iter_range,))
	process.start()
	print('Running...')
	while running():
		check()
	save('Quit', True)
