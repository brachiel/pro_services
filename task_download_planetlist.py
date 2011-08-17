
from datetime import datetime
import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'pro_services.settings'
path = '/home/hyperiums'
if path not in sys.path:
	sys.path.append(path)

from farm_mngr.models import Planet

import urllib
import gzip

download_url = "http://www.hyperiums.com/servlet/HAPI?game=Hyperiums6&player=%s&passwd=%s&request=download&filetype=planets"

opt = dict()

credf = open(path + "/.hyp_cred")
for line in credf.readlines():
	try:
		key, val = line.split('=')
	except ValueError:
		continue

	key = key.strip()
	val = val.strip()

	opt[key] = val
credf.close()

if 'player' not in opt or 'password' not in opt:
	raise Exception("Configuration error: No player/password pair defined in configuration file")

player = opt['player']
password = opt['password']
filename = "planetlist.gz"

stat = os.stat(filename)
fileage = datetime.fromtimestamp(stat.st_mtime)
now = datetime.now()
diff = now - fileage

print "The file is %i hours old" % (diff.seconds / 3600.)
if (diff.seconds / 3600.) >= 23.5: # correction for cronjobs (start time != save time)
	pass
	#urllib.urlretrieve(download_url % (player, password), filename)

f = gzip.GzipFile(filename, "r")

for line in f.readlines():
	line = line.strip()
	if line[0] == '#': continue

	id, name, gov, x, y, race, prod, act, tag, civ, size = line.split(' ')

	id = int(id)
	x = int(x)
	y = int(y)
	race = int(race)
	prod = int(prod)
	act = int(act)
	tag = tag.strip('[]')
	civ = int(civ)

	if not (-881 <= y and y <= -835): # Not SC14
		continue 

	print "%s (%s,%s) [%s]" % (name, x, y, tag)

	try:
		p = Planet.objects.get(pk=id)
		p.name = name
		p.act = act
		p.publictag = tag
		p.civlevel = civ
		p.save()
	except Planet.DoesNotExist:
		p = Planet(id=id, name=name, x=x, y=y, gov=gov, race=race, prod=prod, activity=act, publictag=tag, civlevel=civ)
		p.save()


f.close()

