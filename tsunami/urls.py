
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required

from tsunami.views import BundlesList, Home, Go, SuccessfulDeployment

urlpatterns = patterns(
    '',
    url(r'^$', Home.as_view(), name='home'),
    url(r'^bundles$', BundlesList.as_view(), name='bundles'),
    url(r'^go$', Go.as_view(), name='go'),
    url(r'^successful_deployment/(?P<service_id>[-\w]+)/$', SuccessfulDeployment.as_view(), name='successful_deployment'),
    # url(r'^bundles$', permission_required('tsunami.ik_tsunami_client')(BundlesList.as_view()), name='bundles'),
)
