import json
import logging

from django.views.generic.base import TemplateView

from tsunami.models import Bundle

logger = logging.getLogger('ikwen')


class Home(TemplateView):
    template_name = 'tsunami/tsunami_homepage.html'


class Maintenance(TemplateView):
    template_name = 'tsunami/maintenance.html'


class Bundles(TemplateView):
    template_name = 'tsunami/tsunami_bundles.html'

    def get_context_data(self, **kwargs):
        context = super(Bundles, self).get_context_data(**kwargs)
        bundles_list = Bundle.objects.filter(is_active=True).order_by('-id')
        context['bundles_list'] = bundles_list
        return context

    def get(self, request, *args, **kwargs):
        action = request.GET.get('action')
        if action == 'get_bundle':
            return self.get_bundle(request)
        return super(Bundles, self).get(request, *args, **kwargs)

    def get_bundle(self, request):
        pass