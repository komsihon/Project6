from threading import Thread

from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.utils.http import urlquote
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView

from ikwen.accesscontrol.backends import UMBRELLA
from ikwen.billing.mtnmomo.views import MTN_MOMO
from ikwen.core.utils import get_service_instance, get_mail_content
from ikwen.core.models import Application
from ikwen.revival.models import MemberProfile


def set_bundle_checkout(request, *args, **kwargs):
    """
    This function has no URL associated with it.
    It serves as ikwen setting "MOMO_BEFORE_CHECKOUT"
    """
    referrer = request.META.get('HTTP_REFERER')
    if request.user.is_anonymous():
        next_url = reverse('ikwen:sign_in')
        if referrer:
            next_url += '?' + urlquote(referrer)
        return HttpResponseRedirect(next_url)
    service = get_service_instance(using=UMBRELLA)
    support_bundle_id = request.POST['support_bundle_id']
    type = request.POST['type']
    bundle = Bundle.objects.using(UMBRELLA).get(pk=bundle_id)
    amount = bundle.cost
    request.session['object_id'] = support_bundle.id

    mean = request.GET.get('mean', MTN_MOMO)
    request.session['mean'] = mean
    request.session['notif_url'] = service.url  # Orange Money only
    request.session['cancel_url'] = referrer  # Orange Money only
    request.session['return_url'] = referrer


def confirm_bundle_payment(request, *args, **kwargs):
    """
    This function has no URL associated with it.
    It serves as ikwen setting "MOMO_AFTER_CHECKOUT"
    """
    service = get_service_instance()
    config = service.config
    refill_id = request.session['object_id']

    member = request.user
    if member.email:
        try:
            subject = _("Get your support code")
            html_content = get_mail_content(subject, template_name='echo/mails/successful_refill.html',
                                            extra_context={'member_name': member.first_name})
            sender = '%s <no-reply@%s>' % (config.company_name, service.domain)
            msg = EmailMessage(subject, html_content, sender, [member.email])
            msg.content_subtype = "html"
            if member != service.member:
                msg.cc = [service.member.email]
            Thread(target=lambda m: m.send(), args=(msg,)).start()
        except:
            pass
    return HttpResponseRedirect(request.session['return_url'])


class Home(TemplateView):
    template_name = 'website/home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        return context

    # def get(self, request, *args, **kwargs):
    #     customer = self.request.user
    #     if customer.is_authenticated():
    #         pending_campaigns = ComCampaign.objects.filter(member=customer, status=ComCampaign.PAID)
    #         if pending_campaigns:
    #             campaign = pending_campaigns[0]
    #             return HttpResponseRedirect(reverse('tsunami:checkout', kwargs={'campaign_id': campaign.id}))
    #     return render(self.request, self.template_name, self.get_context_data())

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            next_url = reverse('ikwen:console')
            return HttpResponseRedirect(next_url)
        return super(Home, self).get(request, *args, **kwargs)


class About(TemplateView):
    template_name = 'website/about.html'


class Bundle(TemplateView):
    template_name = 'website/support_bundle.html'


class Terms(TemplateView):
    template_name = 'core/terms_and_conditions.html'


class Webnode(TemplateView):
    template_name = 'website/apps/webnode.html'

    def get_context_data(self, **kwargs):
        context = super(Webnode, self).get_context_data(**kwargs)
        app = Application.objects.get(slug='webnode')
        context['app'] = app
        return context

    def get(self, request, *args, **kwargs):
        member = request.user
        if member.is_authenticated():
            member_profile, update = MemberProfile.objects.get_or_create(member=member)
            if 'webnode' not in member_profile.tag_list:
                member_profile.tag_list.append('webnode')
        return super(Webnode, self).get(request, *args, **kwargs)


class Kakocase(TemplateView):
    template_name = 'website/apps/kakocase.html'

    def get_context_data(self, **kwargs):
        context = super(Kakocase, self).get_context_data(**kwargs)
        app = Application.objects.get(slug='kakocase')
        context['app'] = app
        return context


class Shavida(TemplateView):
    template_name = 'website/apps/shavida.html'


class PinsView(TemplateView):
    template_name = 'website/apps/pinsview.html'
