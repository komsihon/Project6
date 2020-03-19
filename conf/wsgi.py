import os, sys


path = '/home/w177/MEGAsync/PycharmProjects/ikwenWebsite/conf'
if path not in sys.path:
    sys.path.append(path)

from conf import monitor

monitor.start(interval=1.0)
monitor.track(os.path.join(os.path.dirname(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()