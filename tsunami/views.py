import logging
from threading import Thread


from django.core.mail import EmailMessage
from django.views.generic.base import TemplateView

from ikwen_kakocase.kakocase.models import TsunamiBundle
from ikwen.core.utils import get_service_instance, get_mail_content

from django.utils.translation import gettext as _

logger = logging.getLogger('ikwen')


class Home(TemplateView):
    template_name = 'tsunami/homepage.html'

    def get(self, request, *args, **kwargs):
        action = request.GET.get('action')
        if action == 'send_mail_to_visitor':
            return self.send_mail_to_visitor(request)
        return super(Home, self).get(request, *args, **kwargs)

    def send_mail_to_visitor(self, request):
        service = get_service_instance()
        config = service.config
        visitor_email = request.GET.get('visitor_email')
        try:
            subject = _("Do more with Tsunami !")
            html_content = get_mail_content(subject, template_name='tsunami/mails/first_contact.html',)
            sender = '%s <no-reply@%s>' % (config.company_name, service.domain)
            msg = EmailMessage(subject, html_content, sender, visitor_email)
            msg.content_subtype = "html"
            Thread(target=lambda m: m.send(), args=(msg,)).start()
        except:
            pass


class Maintenance(TemplateView):
    template_name = 'tsunami/maintenance.html'


class BundlesList(TemplateView):
    template_name = 'tsunami/bundle_list.html'

    def get_context_data(self, **kwargs):
        context = super(BundlesList, self).get_context_data(**kwargs)
        bundle_list = TsunamiBundle.objects.filter(is_active=True)
        context['bundle_list'] = bundle_list
        return context

    def get(self, request, *args, **kwargs):
        action = request.GET.get('action')
        if action == 'get_bundle':
            return self.get_bundle(request)
        return super(BundlesList, self).get(request, *args, **kwargs)