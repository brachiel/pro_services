"""This module gathers information from the player via HAPI and saves it to the database"""

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from auth.hapi import HAPI, HAPI_Error
from django.contrib.auth.models import User
from farm_mngr.models import Planet, PlanetDetail, Infiltration, Exploitation, Unit, Fleet, GA, Player

failure = HttpResponse("false", mimetype='application/json')
success = HttpResponse("true", mimetype='application/json')

def create_hapi_connection(profile):
	h = HAPI()
	h.player = profile.user.username
	h.connect()
	h.base_hash = {
		'gameid': profile.gameid,
		'playerid': profile.player.hypid,
		'authkey': profile.authkey }

	return h

@login_required
def planetinfo(request):
	user = request.user
	profile = user.get_profile()

	hapicon = create_hapi_connection(profile)

	try:
		planets = hapicon.getPlanetInfo()
		hapicon.close()
	except HAPI_Error:
		return failure

	# check if data is ok
	if not len(planets.keys()) > 1: # less than 2 planets would be weird
		return failure

	# delete old data
	PlanetDetail.objects.filter(owner=profile.player).delete()

	for planetname, data in planets.items():
		try:
			planet = Planet.objects.get(name=planetname)
		except Planet.DoesNotExist:
			continue

		kwargs = { 'planet': planet, 'user': user, 'owner': profile.player }
		for key in PlanetDetail.hapi_keys:
			kwargs[key] = data[key]

		try:
			planetdetail = planet.planetdetail;

			for key, value in kwargs.items():
				setattr(planetdetail, key, value)

			planetdetail.save()
		except PlanetDetail.DoesNotExist:
			PlanetDetail.objects.create(**kwargs)

	return success


@login_required
def exploitations(request):
	user = request.user
	profile = user.get_profile()

	hapicon = create_hapi_connection(profile)

	try:
		planets = hapicon.getExploitInfo()
		hapicon.close()
	except HAPI_Error:
		return failure

	# check if data is ok
	if not len(planets.keys()) > 1: # less than 2 planets would be weird
		return failure

	for planetname, data in planets.items():
		try:
			planet = Planet.objects.get(name=planetname)

			planet.exploitation_set.all().delete()
		except Planet.DoesNotExist:
			continue

		kwargs = { 'planet': planet, 'user': user, 'owner': profile.player }
		for key in Exploitation.hapi_keys:
			kwargs[key] = data[key]

		Exploitation.objects.create(**kwargs)

	return success



@login_required
def infiltrations(request):
	user = request.user
	profile = user.get_profile()

	hapicon = create_hapi_connection(profile)

	try:
		planets = hapicon.getInfiltrInfo()
		hapicon.close()
	except HAPI_Error:
		return failure

	# delete old data
	Infiltration.objects.filter(user=user).delete()

	for planetname, infiltr_list in planets.items():
		try:
			src_planet = Planet.objects.get(name=planetname)
		except Planet.DoesNotExist:
			continue

		for infiltr in infiltr_list.values():
			try:
				dst_planet = Planet.objects.get(name=infiltr['planetname'])
			except Planet.DoesNotExist:
				continue

			kwargs = { 'src_planet': src_planet,
					   'dst_planet': dst_planet,
					   'user': user }
					   

			for key in Infiltration.hapi_keys:
				kwargs[key] = infiltr[key]

			Infiltration.objects.create(**kwargs)

	return success

@login_required
def fleets_away(request):
	return fleets(request, 'foreign_planets')

@login_required
def fleets(request, data='own_planets'):
	print "FLEETS"
	user = request.user
	profile = user.get_profile()

	hapicon = create_hapi_connection(profile)

	try:
		planets = hapicon.getFleetInfo(data=data)
		hapicon.close()
	except HAPI_Error:
		return failure

	for planetname, details in planets.items():
		try:
			planet = Planet.objects.get(name=planetname)
		except Planet.DoesNotExist:
			continue

		try:
			planetdetails = PlanetDetail.objects.get(planet=planet)

			# fleet_base_keys = ['planet','stasis','vacation','isneutral','nrj','nrjmax']

			if details['nrj'] is not None:
				planetdetails.nrj = details['nrj']
				planetdetails.nrjmax = details['nrjmax']

			if details['isneutral'] is not None:
				planetdetails.isneutral = details['isneutral']

			planetdetails.stasis = details['stasis']
			
			planetdetails.user = user # user who gave the last information
			planetdetails.save()
		except PlanetDetail.DoesNotExist:
			PlanetDetail.objects.create(planet=planet, user=user, nrj=details['nrj'], nrjmax=details['nrjmax'],
										isneutral=details['isneutral'], stasis=details['stasis'])

		has_fleet = False
		has_gas = False

		seen_fleets = [] # To delete unseen fleets
		for fleetinfo in details['fleets']:
			seen_fleets.append(fleetinfo['fleetid'])
			
			kwargs = { 'user': user, 'planet': planet }
			is_fleet = None # false=gas, true=fleet

			if fleetinfo['owner'] is None or fleetinfo['owner'] == '':
				kwargs['owner'] = None
			else:
				try:
					owner = Player.objects.get(name=fleetinfo['owner'])
					kwargs['owner'] = owner
				except Player.DoesNotExist:
					owner = Player(name=fleetinfo['owner'])
					owner.save()
					kwargs['owner'] = owner

			if fleetinfo['scou'] is not None:
				is_fleet = True

				try:
					fleet = Fleet.objects.get(fleetid=fleetinfo['fleetid'])
					fleet.user = user # update user who gave latest information

					if owner is not None: # Maybe we don't have the right to see the owner or it's camouflaged
						fleet.owner = owner

					# Only set these if they are not None.
					for key in Fleet.hapi_keys:
						if fleetinfo[key] is not None:
							setattr(fleet, key, fleetinfo[key])

					fleet.save()
				except Fleet.DoesNotExist:
					for key in Fleet.hapi_keys:
						kwargs[key] = fleetinfo[key]

					for string_key in ['fname']:
						if kwargs[string_key] is None:
							kwargs[string_key] = ''

					Fleet.objects.create(**kwargs)
			else:
				is_fleet = False

				try:
					ga = GA.objects.get(fleetid=fleetinfo['fleetid'])
					ga.user = user # update user who gave latest information

					if owner is not None:
						ga.owner = owner

					# Only set these if they are not None.
					for key in GA.hapi_keys:
						if fleetinfo[key] is not None:
							setattr(ga, key, fleetinfo[key])

					ga.save()
				except GA.DoesNotExist:
					for key in GA.hapi_keys:
						kwargs[key] = fleetinfo[key]

					for string_key in ['fname']:
						if kwargs[string_key] is None:
							kwargs[string_key] = ''

					GA.objects.create(**kwargs)

		# Delete all fleets on this planet that were not seen by us
		Fleet.objects.filter(planet=planet).exclude(fleetid__in=seen_fleets).delete()
		GA.objects.filter(planet=planet).exclude(fleetid__in=seen_fleets).delete()
	# for planet



	return success



