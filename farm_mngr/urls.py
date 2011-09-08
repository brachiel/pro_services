from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('farm_mngr.views',
	url(r'^$', 'user.login'),

	url(r'^user/login/$', 'user.login'),
	url(r'^user/logout/$', 'user.logout'),

	url(r'^data/planetinfo/$','data.planetinfo'),
	url(r'^data/infiltrations/$','data.infiltrations'),
	url(r'^data/exploitations/$','data.exploitations'),
	url(r'^data/fleets/$','data.fleets'),
	url(r'^data/fleets_away/$','data.fleets_away'),

	url(r'^control_panel/$', 'hyp.control_panel'),
	url(r'^update_data/$', 'hyp.update_data'),
	url(r'^farm_list/$', 'hyp.farm_list'),
	url(r'^farm_free_check/$', 'hyp.farm_free_check'),
	url(r'^farm_free_check_json/$', 'hyp.farm_free_check_json'),

	url(r'^reports/map/$', 'map.show_map'),
	url(r'^reports/map/sector/$', 'map.map_sector'),
	url(r'^reports/map/farms/$', 'map.map_get_farms'),
	url(r'^reports/map/units/$', 'map.map_get_units'),

	url(r'^lookup/planet$', 'hyp.lookup_planet'),
)
