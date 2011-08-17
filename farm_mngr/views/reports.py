from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from farm_mngr.models import Planet, Farm

@login_required
def farm_map(request):

	map = { 'max_x': 0, 'min_x': 0, 'max_y': -1000, 'min_y': 0, 'size_x': 0, 'size_y': 0, 'planets': {} }

	for p in Planet.objects.all():
		if map['max_x'] < p.x: map['max_x'] = p.x
		if map['max_y'] < p.x: map['max_y'] = p.y
		if map['min_x'] > p.x: map['min_x'] = p.x
		if map['min_y'] > p.x: map['min_y'] = p.y

		if p.y not in map['planets']:
			map['planets'][p.y] = dict()

		if p.x not in map['planets'][p.y]:
			map['planets'][p.y][p.x] = []

		info = { 'infotags': [] }
		if p.farm_set.count() > 0:
			info['infotags'].append('farm')
			info['owners'] = []

			for f in p.farm_set.all():
				info['owners'].append(f.user.username)

		if p.publictag == 'Pro14':
			info['infotags'].append('pro14')

		info['infotags'] = ' '.join(info['infotags']) # so it can be used as css classes
		
		map['planets'][p.y][p.x].append({'p': p, 'info': info})

	map['size_x'] = map['max_x'] - map['min_x']
	map['size_y'] = map['max_y'] - map['min_y']
	map['x_coords'] = range(map['min_x'], map['max_x'])
	map['y_coords'] = range(map['min_y'], map['max_y'])

	t = loader.get_template('reports/map.html')
	c = RequestContext(request, {'username': user.username, 'map': map })
	return HttpResponse(t.render(c))
