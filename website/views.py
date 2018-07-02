from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.views.generic.base import TemplateView


class Home(TemplateView):
    template_name = 'website/home.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            next_url = reverse('ikwen:console')
            return HttpResponseRedirect(next_url)
        return super(Home, self).get(request, *args, **kwargs)


class About(TemplateView):
    template_name = 'website/about.html'


class Webnode(TemplateView):
    template_name = 'website/apps/webnode.html'


class Kakocase(TemplateView):
    template_name = 'website/apps/kakocase.html'


class Shavida(TemplateView):
    template_name = 'website/apps/shavida.html'


class PinsView(TemplateView):
    template_name = 'website/apps/pinsview.html'
