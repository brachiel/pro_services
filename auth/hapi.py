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

	fleet_base_keys = ['planet','stasis','vacation','isneutral','nrj','nrjmax']
	fleet_keys = ['fleetid','fname','sellprice','frace','owner','defend','camouf','bombing','autodrop','delay',
				  'garmies','carmies','scou','crui','bomb','dest']
	fleet_bools =  ['stasis','vacation','isneutral','defend','camouf','bombing','autodrop']
	fleet_strings =  ['planet','fname','owner']

	def __init__(self):
		self.host = 'www.hyperiums.com'
		self.hapi_url = 'http://www.hyperiums.com/servlet/HAPI?%s'

	def connect(self):
		self.conn = httplib.HTTPConnection(self.host, 80, timeout=10)

	def close(self):
		self.conn.close()

	def auth(self, username, hapikey, game='Hyperiums6'):
		h = {'game': game, 'player': username, 'hapikey': hapikey}
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

	def getFleetInfo(self, planet='*', data='own_planets'):
		h = self.base_hash
		h['request'] = 'getfleetsinfo'
		h['planet'] = planet
		h['data'] = data

		r = self.makeRequest(h)
		
		i = 0
		planet_info = dict()
		while ('planet%i' % i) in r:
			p = r['planet%i' % i]
			planet_info[p] = {'fleets':[]} 

			for key in self.fleet_base_keys:
				try:
					val = r["%s%i" % (key, i)]
				except KeyError:
					planet_info[p][key] = None
					continue

				if key in self.fleet_bools:
					if val == '0':
						planet_info[p][key] = False
					elif val == '1':
						planet_info[p][key] = True
					else:
						planet_info[p][key] = None
				elif key in self.fleet_strings:
					planet_info[p][key] = val
				elif val == '?':
					planet_info[p][key] = None
				else:
					planet_info[p][key] = int(val)

			j = 0
			while ('fleetid%i.%i' % (i,j)) in r:
				fleet = {}

				for key in self.fleet_keys:
					try:
						val = r["%s%i.%i" % (key, i, j)]
					except KeyError:
						fleet[key] = None
						continue

					if key in self.fleet_bools:
						if val == '0':
							fleet[key] = False
						elif val == '1':
							fleet[key] = True
						else:
							fleet[key] = None
					elif key in self.fleet_strings:
						fleet[key] = val
					elif val == '?':
						fleet[key] = None
					else:
						fleet[key] = int(val)

				# If we own the fleet, and the GA number is None, we'll set it to 0
				if fleet['scou'] is not None and fleet['carmies'] is None and fleet['owner'] == self.player:
					fleet['carmies'] = 0

				planet_info[p]['fleets'].append(fleet)
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


if __name__=='__main__':
	import sys
	print "\tlogin: ",
	name = sys.stdin.readline().strip()
	print "\tauthkey: ",
	authkey = sys.stdin.readline().strip()

	h = HAPI()
	h.connect()
	h.auth(name, authkey)
	info = h.getFleetInfo(data='foreign_planets')

	for planet_name, details in info.items():
		print "%s:" % planet_name
		for fleet in details['fleets']:
			if fleet['scou'] is not None:
				# Fleet
				if fleet['carmies'] is not None:
					print "- Fleet %s %i %i %i %i (%i)" % (fleet['owner'], fleet['crui'], fleet['dest'], fleet['bomb'], fleet['scou'], fleet['carmies'])
				else:
					print "- Fleet %s %i %i %i %i (?)" % (fleet['owner'], fleet['crui'], fleet['dest'], fleet['bomb'], fleet['scou'])
			else:
				# Army
				if fleet['garmies'] is None:
					print "- GA %s ?" % (fleet['owner'])
				else:
					print "- GA %s %i" % (fleet['owner'], fleet['garmies'])

