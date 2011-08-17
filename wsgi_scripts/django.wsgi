
import os
import sys

paths = ['/home/hyperiums','/home/hyperiums/pro_services']
for path in paths:
	if path not in sys.path:
		sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'pro_services.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

