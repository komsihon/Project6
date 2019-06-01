
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from tsunami.views import BundlesList, Home, ServicesLinks

urlpatterns = patterns(
    '',
    url(r'^$', Home.as_view(), name='home'),
    url(r'^bundles$', BundlesList.as_view(), name='bundles'),
    url(r'^serviceslinks$', ServicesLinks.as_view(), name='serviceslinks'),
)
