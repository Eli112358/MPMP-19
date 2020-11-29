import dbm
import json
import os
import pathlib

data = dict(
	last_checked=0,
	results=[],
	running_total=0,
)
data_path = pathlib.Path('../data')
db = None
primes = None
save_interval = 1000


# todo: use argparse to control save interval and run length
# todo... yet still support indefinite run length (until keyboard interrupt)


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


def save():
	json.dump(data, open(data_path / 'results.json', 'w'), indent='\t')


def check(n):
	prime = next(primes)
	p = prime[1]
	data['running_total'] += p ** 2
	data['last_checked'] = n
	if data['running_total'] % n == 0:
		data['results'].append(n)
		print(n)
	if n % save_interval == 0:
		save()


if __name__ == '__main__':
	print('Loading...')
	try:
		if not os.path.isdir(data_path):
			os.makedirs(data_path)
		data = json.load(open(data_path / 'results.json'))
	except FileNotFoundError:
		save()
	db = dbm.open(str(data_path / 'generator.db'), 'c')
	print('Done')
	primes = get_primes()
	running = True
	while running:
		try:
			check(data['last_checked'] + 1)
		except KeyboardInterrupt:
			running = False
	print('Saving...')
	save()
	db.close()
	print('Done')
