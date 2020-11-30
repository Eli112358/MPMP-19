import json


def get_primes():
	"""
	Sieve of Eratosthenes
	From https://stackoverflow.com/a/568618/2640292
	"""
	d, q = {}, 2
	while True:
		if q not in d:
			yield q
			d[q * q] = [q]
		else:
			for n in d[q]:
				d.setdefault(n + q, []).append(n)
			del d[q]
		q += 1


def get_primes_dbm(db):
	"""
	Sieve of Eratosthenes
	From https://stackoverflow.com/a/568618/2640292

	This implementation, however, reads and stores its variables to disk via dbm
	This is so we can resume the computation where it left off, every time it is called

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

	i(), q()
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
