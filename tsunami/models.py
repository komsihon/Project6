import os

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from djangotoolbox.fields import ListField, EmbeddedModelField
from django.db import models
from ikwen.core.utils import to_dict

from ikwen.accesscontrol.models import Member
from ikwen.billing.models import MoMoTransaction
from ikwen.core.fields import MultiImageField
from ikwen.core.models import Model
from django import forms


class StringListField(forms.CharField):
    def prepare_value(self, value):
        return ', '.join(value)

    def to_python(self, value):
        if not value:
            return []
        return [item.strip() for item in value.split(',')]


class OptionsField(ListField):
    def formfield(self, **kwargs):
        return models.Field.formfield(self, StringListField, **kwargs)


class BundleType(Model):
    SOCIAL = 'Social marketing'
    FULL = 'Full option'
    BUSINESS = 'Business'

    STATUS_CHOICES = (
        (SOCIAL, _('Social marketing')),
        (FULL, _('Full option')),
        (BUSINESS, _('Business')),
    )
    name = models.CharField(max_length=30, choices=STATUS_CHOICES, default=SOCIAL)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class Bundle(Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, blank=True)
    type = models.ForeignKey(BundleType, blank=True)
    cost = models.IntegerField(help_text=_("Cost per month"))
    website_cost = models.IntegerField(null=True, blank=True, help_text=_("Cost of the website for the current offer"))
    options = OptionsField(help_text=_("Coma separated options"))
    max_img_count = models.IntegerField(default=5, help_text=_("Image count for the offer"))
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class ComCampaign(Model):
    PENDING = 'Pending'
    PAID = 'Paid'
    COMPLETE = 'Complete'
    PROCESSED = 'Processed'

    STATUS_CHOICES = (
        (PENDING, _('Pending')),
        (PAID, _('Paid')),
        (COMPLETE, _('Complete')),
        (PROCESSED, _('Processed'))
    )

    offer = models.ForeignKey(Bundle)
    member = models.ForeignKey(Member, blank=True)
    network_page = models.URLField(max_length=255, blank=True, null=True)
    has_page = models.BooleanField(default=False)
    photos = ListField(EmbeddedModelField('Photo'), editable=False)
    age_range = models.CharField(max_length=255, blank=True,null=True)
    audience_gender = models.CharField(max_length=25, blank=True,null=True)
    location = models.CharField(max_length=25, blank=True,null=True)
    website_needed = models.BooleanField(default=False)
    cost = models.IntegerField(blank=True, null=True, help_text=_("Campaign final cost"))
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=PENDING)

    def __unicode__(self):
        return self.offer.name

    def _get_image(self):
        return self.photos[0].image if len(self.photos) > 0 else None

    image = property(_get_image)

    def get_photos_url_list(self):
        photo_list = []
        for photo in self.photos:
            photo_list.append({
                'original': photo.image.url,
                'small': photo.image.small_url,
                'thumb': photo.image.thumb_url
            })
        return photo_list

    def get_photos_ids_list(self):
        return ','.join([photo.id for photo in self.photos])

    def delete(self, *args, **kwargs):
        for photo in self.photos:
            photo.delete(*args, **kwargs)
        super(ComCampaign, self).delete(*args, **kwargs)


class Photo(models.Model):
    UPLOAD_TO = 'tsunami/photos'
    PLACE_HOLDER = 'no_photo.png'
    image = MultiImageField(upload_to=UPLOAD_TO, max_size=800)

    def delete(self, *args, **kwargs):
        try:
            os.unlink(self.image.path)
            os.unlink(self.image.small_path)
            os.unlink(self.image.thumb_path)
        except:
            pass
        super(Photo, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.image.url


class PromoCode(Model):
    code = models.CharField(max_length=100,
                            help_text=_("Title of the discount coupon"))
    start_on = models.DateTimeField(help_text=_("First day of the discount coupon"))
    end_on = models.DateTimeField(help_text=_("Last day of the discount coupon"))
    rate = models.SmallIntegerField(help_text=_("Discount coupon percentage"))
    is_active = models.NullBooleanField(default=True,
                                 help_text=_("Allow to activate or no the promo code"))

    def to_dict(self):
        var = to_dict(self)
        var['created_on'] = naturaltime(self.created_on)
        var['updated_on'] = naturaltime(self.updated_on)
        var['start_on'] = naturaltime(self.start_on)
        var['end_on'] = naturaltime(self.end_on)
        return var

