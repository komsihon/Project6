from django.conf.urls import patterns, include, url

from django.contrib import admin
# from ikwen.flatpages.views import FlatPageView

from website.views import Home, About, Webnode, Kakocase, Shavida, PinsView, Terms

admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^$', Home.as_view(), name='home'),
    url(r'^about$', About.as_view(), name='about'),
    url(r'^terms$', Terms.as_view(), name='terms_and_conditions'),
    url(r'^webnode$', Webnode.as_view(), name='webnode'),
    url(r'^kakocase$', Kakocase.as_view(), name='kakocase'),
    url(r'^shavida$', Shavida.as_view(), name='shavida'),
    url(r'^pinsview$', PinsView.as_view(), name='pins_view'),
    url(r'^tsunami/', include('tsunami.urls', namespace='tsunami')),
    url(r'^laakam/', include(admin.site.urls)),
    url(r'^billing/', include('ikwen.billing.urls', namespace='billing')),
    # url(r'^cashout/', include('ikwen.cashout.urls', namespace='cashout')),
    # url(r'^retail/', include('ikwen.partnership.urls', namespace='partnership')),
    # url(r'^theming/', include('ikwen.theming.urls', namespace='theming')),
    url(r'^kakocase/', include('ikwen_kakocase.kakocase.urls', namespace='kakocase')),
    # url(r'^shavida/', include('ikwen_shavida.shavida.urls', namespace='shavida')),
    # url(r'^webnode/', include('ikwen_webnode.webnode.urls', namespace='webnode')),
    url(r'^', include('ikwen.core.urls', namespace='ikwen')),
    # url(r'^page/(?P<url>[-\w]+)/$', FlatPageView.as_view(), name='flatpage'),
)

