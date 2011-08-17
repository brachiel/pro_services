from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
#from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
#from django.db import IntegrityError
from farm_mngr.models import HypUserProfile

#import re

def login(request):
	t = loader.get_template('user/login.html')
	c = RequestContext(request, {})

	def response(rc):
		return HttpResponse(t.render(rc))

	if request.user.is_authenticated():
		#return HttpResponse("You're already logged in as %s. Log out first." % request.user.username)
		return HttpResponseRedirect('/pro_services/control_panel/')
	elif 'login' in request.POST:
		try:
			username = request.POST['username']
			hapikey = request.POST['hapikey']
		except KeyError:
			c['error_message'] = 'Invalid or missing username or password'
			return response(c)

		user = authenticate(username=username, hapikey=hapikey)
		if user is not None:
			if user.is_active:
				auth_login(request, user)

				if 'next' in request.GET:
					return HttpResponseRedirect(request.GET['next'])
				else:
					return HttpResponseRedirect('/pro_services/control_panel/')
				
				#return HttpResponse("You're logged in as %s with authkey %s." % (user.username, user.get_profile().authkey))
			else:
				c['error_message'] = "The account %s has been disabled." % user.username
				return response(c)
		else:
			c['error_message'] = "The authentication failed."
			return response(c)

#	elif 'register' in request.POST:
#		try:
#			username = request.POST['username']
#			password = request.POST['password']
#			password2 = request.POST['password2']
#		except KeyError:
#			c['error_message'] = 'Invalid or missing username or password(s)'
#			return response(c)
#
#		try:
#			email = request.POST['email']
#		except KeyError:
#			email = ''
#
#		if not password == password2:
#			c['error_message'] = "The two passwords you've given do not match."
#			c['username'] = username
#			c['email'] = email
#			return response(c)
#
#		try:
#			user = User.objects.create_user(username, email, password)
#		except IntegrityError:
#			c['error_message'] = 'Your username was not valid (maybe it already exists?).'
#			return response(c)
#
#		auser = authenticate(username=username, password=password)
#		auth_login(request, auser)
#
#		return HttpResponse("You're now registered as %s." % auser.username)
	else:
		return response(c)


def logout(request):
	if request.user.is_authenticated:
		try:
			p = request.user.get_profile()
			p.hapikey = ''
			p.authkey = ''
			p.save()
		except HypUserProfile.DoesNotExist:
			pass

		auth_logout(request)
		return HttpResponseRedirect('/pro_services/user/login/')
	else:
		return HttpResponseRedirect('/pro_services/user/login/')
		

