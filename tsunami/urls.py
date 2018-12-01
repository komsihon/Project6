
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required

from tsunami.views import Bundles, Home

urlpatterns = patterns(
    '',
    url(r'^$', Home.as_view(), name='home'),
    url(r'^bundles$', Bundles.as_view(), name='bundles'),
    # url(r'^bundles$', permission_required('tsunami.ik_tsunami_client')(Bundles.as_view()), name='bundles'),
)
