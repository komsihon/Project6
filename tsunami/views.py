import json
import logging
from threading import Thread

from django.core.exceptions import MultipleObjectsReturned
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView
from ikwen_kakocase.kakocase.models import TsunamiBundle

from ikwen.accesscontrol.models import Member, DEFAULT_GHOST_PWD
from ikwen.core.utils import get_service_instance, get_mail_content
from ikwen.revival.models import ProfileTag, MemberProfile
from ikwen.core.models import Service

TSUNAMI = 'tsunami'
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
        if not visitor_email:
            response = {'error': 'No Email found'}
            return HttpResponse(json.dumps(response), 'content-type: text/json')
        try:
            member = Member.objects.get(email=visitor_email)
        except MultipleObjectsReturned:
            member = Member.objects.filter(email=visitor_email)[0]
        except Member.DoesNotExist:
            username = visitor_email
            member = Member.objects.create_user(username, DEFAULT_GHOST_PWD, email=visitor_email, phone=visitor_email,
                                                is_ghost=True)
        tag_fk_list = []
        tag = TSUNAMI
        tsunami_tag = ProfileTag.objects.get(slug=tag)
        tag_fk_list.append(tsunami_tag.id)
        member_profile, update = MemberProfile.objects.get_or_create(member=member)
        member_profile.tag_fk_list.extend(tag_fk_list)
        member_profile.save()

        try:
            subject = _("Do more with Tsunami !")
            html_content = get_mail_content(subject, template_name='tsunami/mails/first_contact.html', )
            sender = '%s <no-reply@%s>' % (config.company_name, service.domain)
            msg = EmailMessage(subject, html_content, sender, visitor_email)
            msg.content_subtype = "html"
            Thread(target=lambda m: m.send(), args=(msg,)).start()
        except:
            pass
        next_url = reverse('tsunami:bundles')
        return HttpResponseRedirect(next_url)


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
