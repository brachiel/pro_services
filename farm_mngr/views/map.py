from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core import serializers
from django.utils import simplejson
from django.contrib.auth.decorators import login_required, permission_required

from farm_mngr.models import Planet, PlanetDetail, Exploitation, Infiltration, Player, Fleet, GA
from farm_mngr.views.hyp import get_farms

json_serializer = serializers.get_serializer("json")()

@permission_required('farm_mngr.map_show')
def show_map(request):
	user = request.user

	t = loader.get_template('reports/map.html')
	c = RequestContext(request, {'username': user.username,
								 'base_map_url': '/pro_services/reports/map/',
								 'territories': {'MPK':   [-835,  3, -850,   1],
								 				 'BuNnY': [-864, -6, -885, -30],
												 'HIPPI': [-830, 30, -857,   4]},
								 'map_presets': ['SC14 core', 'SC14', 'SC5', 'SC10']}); # predefined map sets
	return HttpResponse(t.render(c))


@permission_required('farm_mngr.map_show')
def map_sector(request):
	get_options = ['min_x','min_y','max_x','max_y']
	mandatory_options = ['min_y','max_y']
	if not set(mandatory_options) <= set(request.GET.keys()): # if GET doesn't contain all mandatory keys
		#return HttpResponse("false", mimetype='application/json')
		return HttpResponse(' '.join(request.GET.keys()), mimetype='text/plain')

	o = {}
	for opt in get_options:
		if opt in request.GET:
			o[opt] = int(request.GET[opt])
		else:
			o[opt] = None

	planets = Planet.objects.filter(y__gte=o['min_y'], y__lte=o['max_y'])
	if o['min_x']: planets = planets.filter(x__gte=o['min_x'])
	if o['max_x']: planets = planets.filter(x__lte=o['max_x'])

	return HttpResponse(json_serializer.serialize(planets, ensure_ascii=False), mimetype='application/json')

@permission_required('farm_mngr.map_show')
@permission_required('farm_mngr.infiltr_report')
@permission_required('farm_mngr.expl_report')
def map_get_farms(request):
	get_options = ['min_x','min_y','max_x','max_y']
	mandatory_options = ['min_y','max_y']
	if not set(mandatory_options) <= set(request.GET.keys()): # if GET doesn't contain all mandatory keys
		return HttpResponse('"You must provide the following attributes: '+', '.join(mandatory_options)+'"', mimetype='application/json')
		#return HttpResponse(' '.join(request.GET.keys()), mimetype='text/plain')

	o = {}
	for opt in get_options:
		if opt in request.GET:
			o[opt] = int(request.GET[opt])
		else:
			o[opt] = None

	planets = get_farms()

	planet_extra_data = {}
	for planet in planets:
		owner = None
		try:
			infil = planet.infiltration_dst.get(captive=True)
			owner = infil.src_planet.planetdetail.owner
		except Infiltration.DoesNotExist:
			pass
		except PlanetDetail.DoesNotExist:
			print "DEBUG 1: That should never happen"
			owner = infil.user.get_profile().player # that should never happen; but well...

		try:
			owner = planet.exploitation_set.get().owner
		except Exploitation.DoesNotExist:
			pass
			
		planet_extra_data[planet.id] = { 'owner': unicode(owner) }
			

	return HttpResponse(simplejson.dumps(planet_extra_data), mimetype='application/json')

@permission_required('farm_mngr.map_show')
@permission_required('farm_mngr.unit_report')
def map_get_units(request):
	get_options = ['min_x','min_y','max_x','max_y','owner']
	mandatory_options = ['min_y','max_y']
	if not set(mandatory_options) <= set(request.GET.keys()): # if GET doesn't contain all mandatory keys
		return HttpResponse("false", mimetype='application/json')
		#return HttpResponse(' '.join(request.GET.keys()), mimetype='text/plain')

	o = {}
	for opt in get_options:
		if opt in request.GET:
			o[opt] = int(request.GET[opt])
		else:
			o[opt] = None

	gas = GA.objects.filter(planet__y__gte=o['min_y'], planet__y__lte=o['max_y'])
	fleets = Fleet.objects.filter(planet__y__gte=o['min_y'], planet__y__lte=o['max_y'])
	if o['max_x'] is not None:
		gas = gas.filter(planet__x__lte=o['max_x'])
		fleets = fleets.filter(planet__x__lte=o['max_x'])
	if o['min_x'] is not None:
		gas = gas.filter(planet__x__gte=o['min_x'])
		fleets = fleets.filter(planet__x__gte=o['min_x'])

	if o['owner'] is not None:
		try:
			player = Player.objects.get(name=o['owner'])
		except Player.DoesNotExist:
			return HttpResponse('{error: "owner does not exist"}', mimetype='application/json')

		gas = gas.filter(owner=player)
		fleets = fleets.filter(owner=player)

	ga_keys = ['fleetid','fname','frace','defend','camouf'] + ['garmies']
	fleet_keys =  ['fleetid','fname','frace','defend','camouf'] + \
				  ['bombing', 'autodrop', 'delay', 'carmies', 'crui', 'dest', 'bomb', 'scou']

	units = {'gas': [], 'fleets': []}
	for ga in gas.all():
		unit_datum = {}
		unit_datum['owner'] = unicode(ga.owner)
		unit_datum['planet'] = ga.planet_id

		for key in ga_keys:
			unit_datum[key] = getattr(ga, key)

		units['gas'].append(unit_datum)

	for fleet in fleets.all():
		unit_datum = {}
		unit_datum['owner'] = unicode(fleet.owner)
		unit_datum['planet'] = fleet.planet_id

		for key in fleet_keys:
			unit_datum[key] = getattr(fleet, key)

		units['fleets'].append(unit_datum)

	return HttpResponse(simplejson.dumps(units), mimetype='application/json')

