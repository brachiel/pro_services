from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class HypUserProfile(models.Model):
	user = models.OneToOneField(User)

	gameid = models.IntegerField()
	gameid.null = True
	gameid.blank = True
	playerid = models.IntegerField()
	playerid.null = True
	playerid.blank = True
	
	hapikey = models.CharField(max_length=30)
	hapikey.blank = True
	authkey = models.CharField(max_length=30)
	authkey.blank = True

	class Meta:
		permissions = (
			("can_view_reports", "Can see any reports"),
			("can_view_farms", "Can see all Pro farms at once"),
			("can_view_fleet", "Can see detailed fleet information")
		)

# This signal handler will automatically create a HypUserProfile for every user
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        HypUserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)


class Planet(models.Model):
	id = models.IntegerField(unique=True)
	id.primary_key = True
	name = models.CharField(max_length=50, unique=True)

	x = models.SmallIntegerField()
	y = models.SmallIntegerField()

	publictag = models.CharField(max_length=5)

	GOV_CHOICES = ((0,'Democratic'),(1,'Authoritarian'),(2,'Dictatorial'))
	gov = models.PositiveSmallIntegerField(choices=GOV_CHOICES)

	RACE_CHOICES = ((0, 'Human'), (1, 'Azterk'), (2, 'Xillor'))
	race = models.PositiveSmallIntegerField(choices=RACE_CHOICES)

	PROD_CHOICES = ((0, 'Agro'), (1, 'Minero'), (2, 'Techno'))
	prod = models.PositiveSmallIntegerField(choices=PROD_CHOICES)

	activity = models.IntegerField()
	civlevel = models.PositiveSmallIntegerField()
	civlevel.default = 1

	def __unicode__(self):
		if self.publictag:
			return "%s (%i,%i) [%s]" % (self.name, self.x, self.y, self.publictag)
		else:
			return "%s (%i,%i)" % (self.name, self.x, self.y)

class PlanetDetail(models.Model):
	planet = models.OneToOneField(Planet, primary_key=True)
	user = models.ForeignKey(User)
	last_updated = models.DateTimeField(auto_now=True)

	hapi_keys = ['tax','exploits','nrj','nrjmax','purif','parano','bhole','stasis','factories']

	tax = models.PositiveSmallIntegerField()
	exploits = models.PositiveSmallIntegerField()
	nrj = models.PositiveSmallIntegerField()
	nrjmax = models.PositiveSmallIntegerField()
	purif = models.BooleanField()
	parano = models.BooleanField()
	bhole = models.BooleanField()
	stasis = models.BooleanField()
	factories = models.PositiveSmallIntegerField()

	__unicode__ = Planet.__unicode__


class Infiltration(models.Model):
	user = models.ForeignKey(User)
	last_updated = models.DateTimeField(auto_now=True)

	hapi_keys = ['infid', 'level', 'security', 'growing', 'captive', 'tax', 'income', 'purif']

	dst_planet = models.ForeignKey(Planet, related_name='infiltration_dst') # destination planet
	src_planet = models.ForeignKey(Planet, related_name='infiltration_src') # source planet (planet being infiltrated)

	infid = models.IntegerField(unique=True, primary_key=True)
	level = models.PositiveSmallIntegerField()
	security = models.PositiveSmallIntegerField()
	growing = models.BooleanField()
	captive = models.BooleanField()
	tax = models.PositiveSmallIntegerField(null=True,blank=True)
	income = models.IntegerField(null=True,blank=True)
	purif = models.NullBooleanField()

	def __unicode__(self):
		if self.captive:
			return "%s -> %s (captive)" % (self.src_planet.name, self.dst_planet.name)
		else:
			return "%s -> %s (%i/%i)" % (self.src_planet.name, self.dst_planet.name, self.level, self.security)
			

class Exploitation(models.Model):
	user = models.ForeignKey(User)
	last_updated = models.DateTimeField(auto_now=True)

	hapi_keys = ['nbexp']

	planet = models.ForeignKey(Planet)
	nbexp = models.IntegerField() # no. of exploitations

	def __unicode__(self):
		return "%s - %i" % (self.planet.name, self.nbexp)


