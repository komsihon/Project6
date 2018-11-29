from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.views.generic.base import TemplateView

from ikwen.core.models import Application


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
