from django.conf.urls import patterns, include, url
from django.contrib import admin

from ikwen.core.views import Offline

from ikwen_foulassi.foulassi.views import Home as MyKids, HomeSaaS as ScolarFleet

from website.views import Home, About, Webnode, Kakocase, KakocaseFaq, Shavida, PinsView, Terms, Bundle, ServiceIndexes

admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^$', Home.as_view(), name='home'),
    url(r'^offline.html$', Offline.as_view(), name='offline'),
    url(r'^about$', About.as_view(), name='about'),
    url(r'^support_bundle$', Bundle.as_view(), name='support_bundle'),
    url(r'^terms$', Terms.as_view(), name='terms_and_conditions'),
    url(r'^serviceIndexes/(?P<start>[\d]+)/$', ServiceIndexes.as_view(), name='service_indexes'),
    url(r'^webnode/$', Webnode.as_view(), name='webnode'),
    url(r'^kakocase/$', Kakocase.as_view(), name='kakocase'),
    url(r'^kakocase/faq$', KakocaseFaq.as_view(), name='kakocase_faq'),
    # url(r'^shavida/$', Shavida.as_view(), name='shavida'),
    url(r'^pinsview/$', PinsView.as_view(), name='pinsview'),
    url(r'^tsunami/', include('tsunami.urls', namespace='tsunami')),
    url(r'^laakam/', include(admin.site.urls)),
    url(r'^billing/', include('ikwen.billing.urls', namespace='billing')),
    url(r'^theming/', include('ikwen.theming.urls', namespace='theming')),
    url(r'^kakocase/', include('ikwen_kakocase.kakocase.urls', namespace='kakocase')),
    url(r'^kako/', include('ikwen_kakocase.kako.urls', namespace='kako')),
    url(r'^rewarding/', include('ikwen.rewarding.urls', namespace='rewarding')),
    url(r'^partnership/', include('ikwen.partnership.urls', namespace='partnership')),
    url(r'^revival/', include('ikwen.revival.urls', namespace='revival')),
    url(r'^webnode/', include('ikwen_webnode.webnode.urls', namespace='webnode')),
    url(r'^smartevent/', include('smartevent.urls', namespace='smartevent')),

    # Foulassi URLs
    url(r'^scolarfleet$', ScolarFleet.as_view(), name='scolarfleet'),
    url(r'^mykids$', MyKids.as_view(), name='mykids'),
    url(r'^foulassi/', include('ikwen_foulassi.foulassi.urls', namespace='foulassi')),

    # Echo URLs
    url(r'^echo/', include('echo.urls', namespace='echo')),

    # Daraja URLs
    url(r'^daraja/', include('daraja.urls', namespace='daraja')),

    # STAFF URLs


    url(r'^', include('ikwen.core.urls', namespace='ikwen')),
    # url(r'^page/(?P<url>[-\w]+)/$', FlatPageView.as_view(), name='flatpage'),
)

