import httplib
import urllib
import urlparse

class HAPI_AuthFailed(Exception):
	pass

class HAPI_Error(Exception):
	pass

class HAPI(object):
	planet_keys = ['planet','x','y','size','orbit','gov','govd','ptype','tax','exploits','expinpipe','activity','pop',
			        'race','nrj','nrjmax','purif','parano','block','bhole','stasis','nexus','ecomark','planetid',
					'publictag','factories','civlevel','defbonus','tag1_','tag2_']
	exploit_keys = ['planet','planetid','nbexp','inpipe','tobedem','nbonsale','sellprice','rentability']
	infiltr_keys = ['infid','planetname','tag','x','y','level','security','growing','captive','ptype','race','gov',
					'ownername','tax','income','purif']
	infiltr_bools = ['growing','captive','purif']

	def __init__(self):
		self.host = 'www.hyperiums.com'
		self.hapi_url = 'http://www.hyperiums.com/servlet/HAPI?%s'

	def connect(self):
		self.conn = httplib.HTTPConnection(self.host, 80, timeout=10)

	def close(self):
		self.conn.close()

	def auth(self, username, hapikey):
		h = {'game': 'Hyperiums6', 'player': username, 'hapikey': hapikey}
		r = self.makeRequest(h)

		try:
			self.gameid = r['gameid']
			self.playerid = r['playerid']
			self.authkey = r['authkey']

			self.base_hash = {
				'gameid': self.gameid,
				'playerid': self.playerid,
				'authkey': self.authkey }

			return self.base_hash
		except KeyError: # Authentication error
			self.conn.close()
			raise HAPI_AuthFailed("Auth failed")

	def getPlanetInfo(self, planet='*'):
		h = self.base_hash
		h['request'] = 'getplanetinfo'
		h['planet'] = planet
		h['data'] = 'general'

		r = self.makeRequest(h)
		
		i = 0
		planet_info = dict()
		while ('planet%i' % i) in r:
			keys = self.planet_keys

			p = r['planet%i' % i]
			planet_info[p] = dict()
			for k in keys:
				try:
					planet_info[p][k] = r["%s%i" % (k, i)]
				except KeyError:
					planet_info[p][k] = None

			i += 1

		return planet_info

	def getExploitInfo(self):
		h = self.base_hash
		h['request'] = 'getexploitations'

		r = self.makeRequest(h)
		i = 0
		exploit_info = dict()
		while ('planet%i' % i) in r:
			keys = self.exploit_keys

			p = r['planet%i' % i]
			exploit_info[p] = dict()
			for k in keys:
				try:
					exploit_info[p][k] = r["%s%i" % (k, i)]
				except KeyError:
					exploit_info[p][k] = None

			i += 1

		return exploit_info

	def getInfiltrInfo(self, planet='*'):
		h = self.base_hash
		h['request'] = 'getplanetinfo'
		h['planet'] = planet
		h['data'] = 'infiltr'

		r = self.makeRequest(h)
		
		i = 0
		planet_info = dict()
		while ('planet%i' % i) in r:
			p = r['planet%i' % i]
			planet_info[p] = {} 

			j = 0

			while ('infid%i.%i' % (i,j)) in r:
				keys = self.infiltr_keys 

				infiltr = {}
				for k in keys:
					try:
						infiltr[k] = r["%s%i.%i" % (k, i, j)]
					except KeyError:
						infiltr[k] = None

				for k in ['income','ownername']:
					if infiltr[k] == '?':
						infiltr[k] = None

				for k in self.infiltr_bools:
					if infiltr[k] == '0':
						infiltr[k] = False
					elif infiltr[k] == '1':
						infiltr[k] = True
					else:
						infiltr[k] = None

				planet_info[p][infiltr['planetname']] = infiltr

				j += 1

			i += 1

		return planet_info



	def makeRequest(self, hash):
		get_str = urllib.urlencode(hash)

		req = self.conn.request('GET', self.hapi_url % get_str)
		resp = self.conn.getresponse()

		if resp.status != 200:
			print "Something went wrong."
			raise HAPI_Error("Hyperiums answered with invalid response status.")

		data = resp.read()

		hash_response = urlparse.parse_qs(data, True)
		for key, value in hash_response.items():
			hash_response[key] = value[0]

		if 'error' in hash_response:
			raise HAPI_Error(hash_response['error'])

		return hash_response


