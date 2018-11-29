
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required, login_required

from tsunami.views import find_promo_code, Maintenance,Bundles, Checkout, item_photo_uploader, delete_photo, Home, CCI, \
    get_member_cumulated_coupon, save_cloud_cashin_payment

urlpatterns = patterns(
    '',
    url(r'^$', Home.as_view(), name='home'),
    url(r'^bundles$', Bundles.as_view(), name='bundles'),
    url(r'^checkout/(?P<campaign_id>[-\w]+)/$', login_required(Checkout.as_view()), name='checkout'),
    url(r'^item_photo_uploader$', item_photo_uploader, name='item_photo_uploader'),
    url(r'^delete_photo$', delete_photo, name='delete_photo'),
    url(r'^find_promo_code$', find_promo_code, name='find_promo_code'),
    url(r'^maintenance$', Maintenance.as_view(), name='mainte'),
    url(r'^cashin', login_required(CCI.as_view()), name='cci'),
    url(r'^get_user_coupon', get_member_cumulated_coupon, name='get_user_coupon'),
    url(r'^save_cci', save_cloud_cashin_payment, name='save_cci'),
)