"""This module gathers information from the player via HAPI and saves it to the database"""

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from auth.hapi import HAPI, HAPI_Error
from farm_mngr.models import Planet, PlanetDetail, Infiltration, Exploitation

failure = HttpResponse("false", mimetype='application/json')
success = HttpResponse("true", mimetype='application/json')

def create_hapi_connection(profile):
	h = HAPI()
	h.connect()
	h.base_hash = {
		'gameid': profile.gameid,
		'playerid': profile.playerid,
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
	PlanetDetail.objects.filter(user=user).delete()

	for planetname, data in planets.items():
		try:
			planet = Planet.objects.get(name=planetname)
		except Planet.DoesNotExist:
			continue

		kwargs = { 'planet': planet, 'user': user }
		for key in PlanetDetail.hapi_keys:
			kwargs[key] = data[key]

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

	# delete old data
	Exploitation.objects.filter(user=user).delete()

	for planetname, data in planets.items():
		try:
			planet = Planet.objects.get(name=planetname)
		except Planet.DoesNotExist:
			continue

		kwargs = { 'planet': planet, 'user': user }
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



