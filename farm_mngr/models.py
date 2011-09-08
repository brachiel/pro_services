from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Player(models.Model):
	hypid = models.IntegerField(unique=True, null=True)
	name = models.CharField(max_length=30, unique=True)

	def __unicode__(self):
		return self.name


class HypUserProfile(models.Model):
	user = models.OneToOneField(User)

	gameid = models.IntegerField(null=True, blank=True)
	player = models.OneToOneField(Player)
	
	hapikey = models.CharField(max_length=30, blank=True)
	authkey = models.CharField(max_length=30, blank=True)

	class Meta:
		permissions = (
			("map_show", "Use map"),
		)

# This signal handler will automatically create a HypUserProfile for every user
def create_user_profile(sender, instance, created, **kwargs):
    if created:
		try:
			player = Player.objects.get(name=instance.username)
		except Player.DoesNotExist:
			player = Player(name=instance.username)
			player.save()

		HypUserProfile.objects.create(user=instance, player=player)
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

	class Meta:
		managed = False

	def __unicode__(self):
		if self.publictag:
			return "%s (%i,%i) [%s]" % (self.name, self.x, self.y, self.publictag)
		else:
			return "%s (%i,%i)" % (self.name, self.x, self.y)

class PlanetDetail(models.Model):
	planet = models.OneToOneField(Planet, primary_key=True)
	user = models.ForeignKey(User, related_name='planet_intel') # User who provided the intel
	last_updated = models.DateTimeField(auto_now=True)

	isneutral = models.NullBooleanField()
	isneutral.default = None

	hapi_keys = ['tax','exploits','nrj','nrjmax','purif','parano','bhole','stasis','factories']

	owner = models.ForeignKey(Player, null=True, related_name='planets')
	tax = models.PositiveSmallIntegerField(null=True)
	exploits = models.PositiveSmallIntegerField(null=True)
	nrj = models.PositiveSmallIntegerField()
	nrjmax = models.PositiveSmallIntegerField()
	purif = models.NullBooleanField()
	parano = models.NullBooleanField()
	bhole = models.NullBooleanField()
	stasis = models.BooleanField()
	factories = models.PositiveSmallIntegerField(null=True)

	def __unicode__(self):
		p = self.planet
		if p.publictag:
			return "%s (%i,%i) [%s]" % (p.name, p.x, p.y, p.publictag)
		else:
			return "%s (%i,%i)" % (p.name, p.x, p.y)

	class Meta:
		permissions = (
			("pdet_report", "Use in reports."),
		)


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

	class Meta:
		permissions = (
			("infiltr_report", "Use in reports."),
		)
			

class Exploitation(models.Model):
	user = models.ForeignKey(User)
	last_updated = models.DateTimeField(auto_now=True)

	hapi_keys = ['nbexp']

	owner = models.ForeignKey(Player, null=True, default=None) # Owner of the Exploits
	planet = models.ForeignKey(Planet)
	nbexp = models.IntegerField() # no. of exploitations

	def __unicode__(self):
		return "%s - %i" % (self.planet.name, self.nbexp)

	class Meta:
		permissions = (
			("expl_report", "Use in reports."),
		)

class Unit(models.Model):
	user = models.ForeignKey(User, related_name='unit_intel_%(class)s') # User who provided intel
	last_updated = models.DateTimeField(auto_now=True)

	hapi_keys = ['fleetid','fname','sellprice','frace','defend','camouf']

	planet = models.ForeignKey(Planet)
	
	fleetid = models.PositiveIntegerField(primary_key=True)
	fname = models.CharField(max_length=30)
	sellprice = models.SmallIntegerField(null=True)

	RACE_CHOICES = ((0, 'Human'), (1, 'Azterk'), (2, 'Xillor'))
	frace = models.PositiveSmallIntegerField(choices=RACE_CHOICES)

	owner = models.ForeignKey(Player, null=True, blank=True, related_name='%(class)ss')

	defend = models.BooleanField()
	camouf = models.BooleanField()
	
	class Meta:
		abstract = True,
		permissions = (
			("unit_report", "Use in reports."),
		)

class Fleet(Unit):
	hapi_keys = Unit.hapi_keys + ['bombing', 'autodrop', 'delay', 'carmies', 'crui', 'dest', 'bomb', 'scou']

	bombing = models.NullBooleanField()
	autodrop = models.NullBooleanField()
	delay = models.NullBooleanField()

	carmies = models.PositiveSmallIntegerField(null=True, blank=True)

	crui = models.PositiveIntegerField()
	dest = models.PositiveIntegerField()
	bomb = models.PositiveIntegerField()
	scou = models.PositiveIntegerField()

class GA(Unit):
	hapi_keys = Unit.hapi_keys + ['garmies']

	garmies = models.PositiveSmallIntegerField(null=True, blank=True)




