from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('farm_mngr.views',
	url(r'^$', 'user.login'),

	url(r'^user/login/$', 'user.login'),
	url(r'^user/logout/$', 'user.logout'),

	url(r'^data/planetinfo/$','data.planetinfo'),
	url(r'^data/infiltrations/$','data.infiltrations'),
	url(r'^data/exploitations/$','data.exploitations'),

	url(r'^control_panel/$', 'hyp.control_panel'),
	url(r'^update_data/$', 'hyp.update_data'),
	url(r'^farm_list/$', 'hyp.farm_list'),
	url(r'^farm_free_check/$', 'hyp.farm_free_check'),
	url(r'^farm_free_check_json/$', 'hyp.farm_free_check_json'),

	url(r'^lookup/planet$', 'hyp.lookup_planet'),
)
