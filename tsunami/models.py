from django.utils.translation import gettext_lazy as _
from djangotoolbox.fields import ListField
from django.db import models

from ikwen.accesscontrol.models import Member
from ikwen.billing.models import MoMoTransaction
from ikwen.core.models import Model
from django import forms

from ikwen.rewarding.models import CumulatedCoupon


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


class Bundle(Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, blank=True)
    CCM_feature = models.CharField(max_length=25, default="Cloud Customer Manager")
    CCI_feature = models.CharField(max_length=15, default="Cloud Cash-In")
    CR_feature = models.CharField(max_length=25, default="Continuous Rewarding")
    CR_feature_specs = models.IntegerField()
    support_feature = models.CharField(max_length=50)
    cost = models.IntegerField(help_text=_("Cost per month"))
    website_cost = models.IntegerField(null=True, blank=True, help_text=_("Cost of the website for the current offer"))
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name
