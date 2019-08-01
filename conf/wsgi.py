import os, sys


sys.path.append('/home/komsihon/Dropbox/PycharmProjects/ikwenWebsite/conf')
from conf import monitor

monitor.start(interval=1.0)
monitor.track(os.path.join(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()