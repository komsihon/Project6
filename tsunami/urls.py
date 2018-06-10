
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required, login_required

from tsunami.views import find_promo_code, Maintenance,Bundles, Checkout, item_photo_uploader, delete_photo
urlpatterns = patterns(
    '',
    url(r'^$', Bundles.as_view(), name='bundles'),
    url(r'^checkout/(?P<campaign_id>[-\w]+)/$', login_required(Checkout.as_view()), name='checkout'),
    url(r'^item_photo_uploader$', item_photo_uploader, name='item_photo_uploader'),
    url(r'^delete_photo$', delete_photo, name='delete_photo'),
    url(r'^find_promo_code$', find_promo_code, name='find_promo_code'),
    url(r'^maintenance$', Maintenance.as_view(), name='mainte'),
)