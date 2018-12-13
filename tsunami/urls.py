
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from tsunami.views import BundlesList, Home, Go, SuccessfulDeployment

urlpatterns = patterns(
    '',
    url(r'^$', Home.as_view(), name='home'),
    url(r'^bundles$', BundlesList.as_view(), name='bundles'),
    url(r'^go$', login_required(Go.as_view()), name='go'),
    url(r'^successful_deployment/(?P<service_id>[-\w]+)/$', login_required(SuccessfulDeployment.as_view()), name='successful_deployment'),
)
