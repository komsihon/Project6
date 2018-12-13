import json
import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.http import urlquote
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView

from ikwen_kakocase.kakocase.models import BusinessCategory, TsunamiBundle
from ikwen.partnership.models import ApplicationRetailConfig

from ikwen.theming.models import Theme, Template

from ikwen.billing.models import CloudBillingPlan, IkwenInvoiceItem, InvoiceEntry, Invoice

from ikwen.core.models import Service, Application
from ikwen.core.utils import get_service_instance

from django.utils.translation import gettext as _
from ikwen.accesscontrol.utils import VerifiedEmailTemplateView
from ikwen.accesscontrol.backends import UMBRELLA
from ikwen.accesscontrol.models import Member

from ikwen_kakocase.kakocase.cloud_setup import deploy, DeploymentForm

logger = logging.getLogger('ikwen')


class Home(TemplateView):
    template_name = 'tsunami/homepage.html'


class Maintenance(TemplateView):
    template_name = 'tsunami/maintenance.html'


class Success(TemplateView):
    template_name = 'tsunami/successful_deployment.html'


class SuccessfulDeployment(TemplateView):
    template_name = 'tsunami/successful_deployment.html'

    def get_context_data(self, **kwargs):
        context = super(SuccessfulDeployment, self).get_context_data(**kwargs)
        service_id = kwargs.pop('service_id')
        service = get_object_or_404(Service, pk=service_id)
        context['invoice'] = Invoice.objects.filter(subscription=service)[0]
        return context


class Go(VerifiedEmailTemplateView):
    template_name = 'tsunami/go.html'

    def get_context_data(self, **kwargs):
        context = super(Go, self).get_context_data(**kwargs)
        context['billing_cycles'] = Service.BILLING_CYCLES_CHOICES
        app = Application.objects.using(UMBRELLA).get(slug='kakocase')
        context['app'] = app
        template_list = list(Template.objects.using(UMBRELLA).filter(app=app))
        context['theme'] = list(Theme.objects.using(UMBRELLA).filter(template__in=template_list))[-1]
        context['can_choose_themes'] = True
        billing_plan_list = CloudBillingPlan.objects.using(UMBRELLA).filter(app=app, partner__isnull=True, is_active=True)
        setup_months_count = 3
        context['ikwen_setup_cost'] = app.base_monthly_cost * setup_months_count
        context['ikwen_monthly_cost'] = app.base_monthly_cost
        context['setup_months_count'] = setup_months_count
        context['billing_plan'] = billing_plan_list[0]
        context['business_category_list'] = BusinessCategory.objects.using(UMBRELLA).all()
        return context

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        form = DeploymentForm(request.POST)
        if form.is_valid():
            app_id = form.cleaned_data.get('app_id')
            project_name = form.cleaned_data.get('project_name')
            business_type = form.cleaned_data.get('business_type')
            billing_cycle = form.cleaned_data.get('billing_cycle')
            billing_plan_id = form.cleaned_data.get('billing_plan_id')
            business_category_id = form.cleaned_data.get('business_category_id')
            bundle_id = form.cleaned_data.get('bundle_id')
            domain = form.cleaned_data.get('domain')
            theme_id = form.cleaned_data.get('theme_id')
            partner_id = form.cleaned_data.get('partner_id')
            app = Application.objects.using(UMBRELLA).get(pk=app_id)
            theme = Theme.objects.using(UMBRELLA).get(pk=theme_id)
            billing_plan = CloudBillingPlan.objects.using(UMBRELLA).get(pk=billing_plan_id)
            business_category = BusinessCategory.objects.using(UMBRELLA).get(pk=business_category_id)
            bundle = TsunamiBundle.objects.using(UMBRELLA).get(pk=bundle_id) if bundle_id else None

            customer = Member.objects.using(UMBRELLA).get(pk=request.user.id)
            setup_cost = billing_plan.setup_cost
            monthly_cost = billing_plan.monthly_cost

            partner = Service.objects.using(UMBRELLA).get(pk=partner_id) if partner_id else None
            invoice_entries = []
            domain_name = IkwenInvoiceItem(label='Domain name')
            domain_name_entry = InvoiceEntry(item=domain_name, short_description=domain)
            invoice_entries.append(domain_name_entry)
            website_setup = IkwenInvoiceItem(label='Website setup', price=billing_plan.setup_cost, amount=setup_cost)
            short_description = "%d products" % billing_plan.max_objects
            website_setup_entry = InvoiceEntry(item=website_setup, short_description=short_description, total=setup_cost)
            invoice_entries.append(website_setup_entry)
            if theme.cost > 0:
                theme_item = IkwenInvoiceItem(label='Website theme', price=theme.cost, amount=theme.cost)
                theme_entry = InvoiceEntry(item=theme_item, short_description=theme.name, total=theme.cost)
                invoice_entries.append(theme_entry)
            i = 0
            while True:
                try:
                    label = request.POST['item%d' % i]
                    amount = float(request.POST['amount%d' % i])
                    if not (label and amount):
                        break
                    item = IkwenInvoiceItem(label=label, amount=amount)
                    entry = InvoiceEntry(item=item, total=amount)
                    invoice_entries.append(entry)
                    i += 1
                except:
                    break
            if getattr(settings, 'DEBUG', False):
                service = deploy(app, customer, business_type, project_name, billing_plan, theme, monthly_cost,
                                 invoice_entries, billing_cycle, domain, business_category, bundle,
                                 partner_retailer=partner)
            else:
                try:
                    service = deploy(app, customer, business_type, project_name, billing_plan, theme, monthly_cost,
                                     invoice_entries, billing_cycle, domain, business_category, bundle,
                                     partner_retailer=partner)
                except Exception as e:
                    context = self.get_context_data(**kwargs)
                    context['error'] = e.message
                    return render(request, 'tsunami/go.html', context)
            next_url = reverse('tsunami:successful_deployment', args=(service.id, ))
            return HttpResponseRedirect(next_url)
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return render(request, 'tsunami/go.html', context)


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