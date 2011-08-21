
from hapi import HAPI, HAPI_AuthFailed, HAPI_Error
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib import messages
from farm_mngr.models import HypUserProfile

class HAPIAuth(ModelBackend):
	"""Return user if login to HAPI is successful; None otherwise"""

	supports_object_permissions = False
	supports_anonymous_user = False
	supports_inactive_user = True

	has_perm = ModelBackend.has_perm

	def authenticate(self, username=None, hapikey=None, request=None):
		try:
			user = User.objects.get(username=username)

			if not user.is_active:
				return None

			hapi = HAPI()
			hapi.connect()

			try:
				base_hash = hapi.auth(username, hapikey)
			except timeout:
				messages.error(request, 'There was an error communicating with Hyperiums. Try again later')
				return None
			except HAPI_AuthFailed:
				messages.error(request, 'Check your HAPI key and maybe create a new one.')
				return None

			if base_hash is None:
				messages.error(request, "The hapi key you provided was invalid. Please check that it's correct")
				return None

			hapi.conn.close()

			try:
				p = user.get_profile()
			except HypUserProfile.DoesNotExist:
				p = HypUserProfile.objects.create(user=user)

			try:
				p.gameid = base_hash['gameid']
				p.playerid = base_hash['playerid']
				p.authkey = base_hash['authkey']
			except KeyError:
				messages.error("There was an internal server error. This shouldn't happen :(. Code: Auth3")


			p.hapikey = hapikey
			p.save()

			return user
		except User.DoesNotExist:
			return None

	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None


