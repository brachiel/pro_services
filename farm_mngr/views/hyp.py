
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
#from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from auth.hapi import HAPI, HAPI_Error
from farm_mngr.models import Planet, Infiltration, Exploitation, PlanetDetail
from farm_mngr.views.user import logout

@login_required
def control_panel(request):
	user = request.user

	t = loader.get_template('control_panel.html')
	c = RequestContext(request, {'username': user.username, 'user_permissions': user.get_all_permissions() })
	return HttpResponse(t.render(c))

@login_required
def update_data(request):
	user = request.user

	t = loader.get_template('update_data.html')
	c = RequestContext(request, 
		{'username': user.username,
		 'tasks': {'planetinfo': "Controlled planets",
		 		   'infiltrations': "Infiltrations",
			 	   'exploitations': "Held exploitations"},
		 'data_base_url': '/pro_services/data/',
		 'time_to_wait': 5, # in s
		})
	return HttpResponse(t.render(c))

# Helper function
def get_farms(user=None):
	try:
		farms = Planet.objects.filter(
			Q(infiltration_from__user=user, 
			  infiltration_from__captive=True, 
			  infiltration_from__income__gt=0, 
			  infiltration_from__tax__gt=0) |
			Q(exploitation__user=user, 
			  exploitation__nbexp__gt=0))
	except Planet.DoesNotExist:
		farms = []

	return farms

@login_required
def farm_list(request):
	user = request.user

	try:
		infiltrations = Infiltration.objects.filter(user=user, captive=True, income__gt=0, tax__gt=0)
	except Infiltration.DoesNotExist:
		infiltrations = []

	try:
		exploitations = Exploitation.objects.filter(user=user, nbexp__gt=0)
	except Exploitation.DoesNotExist:
		exploitations = []

	t = loader.get_template('farm_list.html')
	c = RequestContext(request, {'username': user.username,
								 'exploitations': exploitations, 
								 'infiltrations': infiltrations})
	return HttpResponse(t.render(c))

@login_required
def farm_free_check(request):
	user = request.user

	t = loader.get_template('farm_free_check.html')
	c = RequestContext(request, {'username': user.username})
	return HttpResponse(t.render(c))

@login_required
def farm_free_check_json(request):
	is_free = None
	if request.method == "GET":
		if request.GET.has_key(u'query'):
			value = request.GET[u'query']

			try:
				planet = Planet.objects.get(name=value)

				if planet.exploitation_set.filter(nbexp__gt=0).count() > 0:
					is_free = False
				elif planet.infiltration_dst.filter(captive=True, income__gt=0, tax__gt=0).count() > 0:
					is_free = False
				else:
					is_free = True
			except Planet.DoesNotExist:
				is_free = None

	json = simplejson.dumps(is_free)
	return HttpResponse(json, mimetype='application/json')

@login_required
def lookup_planet(request):
	results = []

	if request.method == "GET":
		if request.GET.has_key(u'query'):
			value = request.GET[u'query']

			if len(value) > 2:
				model_results = Planet.objects.filter(name__icontains=value)
				results = [ x.name for x in model_results ]
	json = simplejson.dumps(results)
	return HttpResponse(json, mimetype='application/json')

