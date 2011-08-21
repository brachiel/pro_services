from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from farm_mngr.models import Planet
from django.core import serializers
from django.contrib.auth.decorators import login_required, permission_required

json_serializer = serializers.get_serializer("json")()

#TODO Restrict all of these to users with permissions
@permission_required('farm_mngr.map_show')
def show_map(request):
	user = request.user

	t = loader.get_template('reports/map.html')
	c = RequestContext(request, {'username': user.username,
								 'base_map_url': '/pro_services/reports/map/',
								 'territories': {'MPK':   [-835,  3, -850,   1],
								 				 'BuNnY': [-864, -6, -885, -30],
												 'HIPPI': [-830, 30, -857,   4]}} )
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
