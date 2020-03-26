
from django.conf.urls import patterns, url

from tsunami.views import BundlesList, Home

urlpatterns = patterns(
    '',
    url(r'^$', Home.as_view(), name='home'),
    url(r'^bundles$', BundlesList.as_view(), name='bundles'),
)
