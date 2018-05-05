import json
import os
from datetime import datetime
from threading import Thread

from ajaxuploader.views import AjaxFileUploader
from django.core.files.base import File
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView
from ikwen_kakocase.shopping.utils import send_order_confirmation_email
from django.utils.translation import gettext as _

from conf import settings
from ikwen.core.utils import DefaultUploadBackend, get_service_instance, get_mail_content
from tsunami.models import ComOffer, ComCampaign, Photo, PromoCode
from ikwen.billing.mtnmomo.views import MTN_MOMO
from ikwen.billing.orangemoney.views import ORANGE_MONEY

import logging
logger = logging.getLogger('ikwen')


class Maintenance(TemplateView):
    template_name = 'tsunami/maintenance.html'


class Bundles(TemplateView):
    template_name = 'tsunami/bundles.html'

    def get_context_data(self, **kwargs):
        context = super(Bundles, self).get_context_data(**kwargs)
        customer = self.request.user
        if customer.is_authenticated():
            pending_campaigns = ComCampaign.objects.filter(member=customer, status=ComCampaign.PAID)
            if pending_campaigns:
                campaign = pending_campaigns[0]
                return HttpResponseRedirect(reverse('tsunami:checkout', kwargs={'campaign_id': campaign.id}))
        bundles = ComOffer.objects.filter(is_active=True)
        context['bundles'] = bundles
        return context


class Checkout(TemplateView):
    template_name = 'tsunami/checkout.html'

    def get_context_data(self, **kwargs):
        context = super(Checkout, self).get_context_data(**kwargs)
        campaign_id = kwargs['campaign_id']
        campaign = get_object_or_404(ComCampaign, pk=campaign_id, status=ComCampaign.PAID)
        context['campaign'] = campaign
        return context

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        has_page = False
        campaign_id = self.request.POST.get('campaign_id')
        photos_ids = self.request.POST.get('photos_ids')
        age_range = request.POST.get('age_range')
        gender = request.POST.get('gender')
        location = request.POST.get('location')
        network_page_url = request.POST.get('network_page')
        photos_ids_list = photos_ids.strip(',').split(',') if photos_ids else []
        if network_page_url:
            has_page = True
        try:
            campaign = get_object_or_404(ComCampaign, pk=campaign_id, status=ComCampaign.PAID)
        except ComOffer.DoesNotExist:
            return HttpResponseRedirect(reverse('tsunami:bundles') + '?Errors=unexisting_offer')
        else:
            campaign.audience_gender = gender
            campaign.age_range = age_range
            campaign.network_page = network_page_url
            campaign.has_page = has_page
            campaign.location = location
            campaign.photos = []
            if len(photos_ids_list) == 0:
                campaign.visible = False  # Items without photo are hidden
            else:
                for photo_id in photos_ids_list:
                    if photo_id:
                        try:
                            photo = Photo.objects.get(pk=photo_id)
                            campaign.photos.append(photo)
                        except:
                            pass
            campaign.status = ComCampaign.COMPLETE
            campaign.save()
            next_url = reverse('tsunami:bundles') + '?success=yes'
            return HttpResponseRedirect(next_url)


def delete_photo(request, *args, **kwargs):
    campaign_id = request.GET.get('item_id')
    photo_id = request.GET['photo_id']
    photo = Photo(id=photo_id)
    if campaign_id:
        campaign = ComCampaign.objects.get(pk=campaign_id)
        if photo in campaign.photos:
            campaign.photos.remove(photo)
            campaign.save()
    try:
        Photo.objects.get(pk=photo_id).delete()
    except:
        pass
    return HttpResponse(
        json.dumps({'success': True}),
        content_type='application/json'
    )


class ItemPhotoUploadBackend(DefaultUploadBackend):
    """
    Ajax upload handler for :class:`items.models.Items` photos
    """
    def upload_complete(self, request, filename, *args, **kwargs):
        path = self.UPLOAD_DIR + "/" + filename
        self._dest.close()
        media_root = getattr(settings, 'MEDIA_ROOT')
        try:
            with open(media_root + path, 'r') as f:
                content = File(f)
                destination = media_root + Photo.UPLOAD_TO + "/" + filename
                photo = Photo()
                photo.image.save(destination, content)
                campaign_id = request.GET.get('campaign_id')
                if campaign_id:
                    try:
                        campaign = ComCampaign.objects.get(pk=campaign_id)
                        campaign.photos.add(photo)
                        campaign.save()
                    except:
                        pass

            os.unlink(media_root + path)
            return {
                'id': photo.id,
                'url': photo.image.small_url
            }
        except IOError as e:
            if getattr(settings, 'DEBUG', False):
                raise e
            return {'error': 'File failed to upload. May be invalid or corrupted image file'}


item_photo_uploader = AjaxFileUploader(ItemPhotoUploadBackend)


def find_promo_code(request, *args, **kwargs):
    code = request.GET.get('code')
    now = datetime.now()
    try:
        promo_code = PromoCode.objects.get(code=code.lower(), rate__gt=0, start_on__lte=now, end_on__gt=now, is_active=True)
    except PromoCode.DoesNotExist:
        response = HttpResponse(json.dumps(
            {'error': 'Invalid promo code',
             'message': 'Invalid promo code',
             }), 'content-type: text/json')
    else:
        request.session['promo_code'] = promo_code.to_dict()
        request.session['promo_rate'] = promo_code.rate
        request.session['promo_code_id'] = promo_code.id
        response = HttpResponse(json.dumps(
            {'success': True,
             'promo_code': promo_code.to_dict(),
             }), 'content-type: text/json')
    return response


def set_checkout(request, *args, **kwargs):
    com_offer_id = request.POST.get('product_id')
    need_website = request.POST.get('website_needed')
    website_needed = True
    if need_website == 'false':
        website_needed = False
    member = request.user
    try:
        choosen_offer = ComOffer.objects.get(pk=com_offer_id)
    except ComOffer.DoesNotExist:
        return HttpResponseRedirect(reverse('tsunami:bundles') + '?Errors=yes')
    else:
        campaign = ComCampaign(member=member, offer=choosen_offer, website_needed=website_needed)
        campaign.save()
    if request.session.get('promo_code'):
        promo_id = request.session.get('promo_code_id')
        try:
            coupon = PromoCode.objects.get(pk=promo_id)
        except PromoCode.DoesNotExist:
            pass
        else:
            offer_cost = choosen_offer.monthly_cost
            if website_needed:
                offer_cost = choosen_offer.monthly_cost + choosen_offer.website_cost
            campaign_cost = offer_cost - (offer_cost * coupon.rate / 100)
            campaign.cost = campaign_cost
            campaign.save()
    else:
        offer_cost = choosen_offer.monthly_cost
        if website_needed:
            offer_cost = choosen_offer.monthly_cost + choosen_offer.website_cost
        campaign.cost = offer_cost
        campaign.save()

    service = get_service_instance()
    request.session['amount'] = campaign.cost
    request.session['model_name'] = 'tsunami.ComCampaign'
    request.session['object_id'] = campaign.id

    mean = request.GET.get('mean', MTN_MOMO)
    if mean == MTN_MOMO:
        request.session['is_momo_payment'] = True
    elif mean == ORANGE_MONEY:
        request.session['notif_url'] = service.url + reverse('tsunami:bundles')
        request.session['return_url'] = service.url + (reverse('tsunami:checkout', kwargs={'campaign_id': campaign.id}))
        request.session['cancel_url'] = service.url + reverse('tsunami:bundles')
        request.session['is_momo_payment'] = False

    logger.info("Initialize payment process of Campaign %s " % (campaign.id))
    subject = _("Initialize payment process")
    send_confirmation_email(subject, request.user.full_name, request.user.email, campaign)


def confirm_checkout(request, *args, **kwargs):
    campaign_id = request.POST.get('campaign_id')
    if not campaign_id:
        campaign_id = request.session['object_id']

    campaign = get_object_or_404(ComCampaign, pk=campaign_id, status=ComCampaign.PENDING)

    campaign.status = ComCampaign.PAID
    campaign.save()
    member = request.user

    if member.is_authenticated():
        buyer_name = member.full_name
        buyer_email = member.email
    else:
        buyer_name = campaign.anonymous_buyer.name
        buyer_email = campaign.anonymous_buyer.email
    logger.info("Order successfully proceeded for the Campaign %s " % (campaign.id))

    subject = _("Order successful")
    send_confirmation_email(subject, buyer_name, buyer_email, campaign)

    next_url = reverse('checkout',  kwargs={'campaign_id': campaign.id})
    request.session.modified = True
    try:
        del request.session['promo_code_id']
    except:
        pass
    try:
        del request.session['promo_code']
    except:
        pass
    try:
        del request.session['promo_rate']
    except:
        pass

    if request.session.get('is_momo_payment'):
        return {'success': True, 'next_url': next_url}
    else:
        return HttpResponseRedirect(next_url)


def send_confirmation_email(subject, buyer_name, buyer_email, order, message=None):
    service = get_service_instance()
    html_content = get_mail_content(subject, '', template_name='tsunami/mails/order_notice.html',
                                    extra_context={'buyer_name': buyer_name, 'order': order, 'message': message})
    sender = '%s <no-reply@%s>' % (service.project_name, service.domain)
    msg = EmailMessage(subject, html_content, sender, [buyer_email])
    bcc = [service.member.email, service.config.contact_email]
    msg.bcc = list(set(bcc))
    msg.content_subtype = "html"
    Thread(target=lambda m: m.send(), args=(msg, )).start()

