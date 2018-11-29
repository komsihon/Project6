from django.contrib.admin import site
from django.contrib import admin
from django.utils.safestring import mark_safe

from models import Bundle, PromoCode, ComCampaign, BundleType


class BundleAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'max_img_count')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


class BundleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)


class ComCampaignAdmin(admin.ModelAdmin):
    list_display = ('member', 'offer', 'age_range', 'status', 'created_on')
    search_fields = ('offer',)
    readonly_fields = ["campaign_image"]

    def campaign_image(self, obj):
        p = []
        for photo in obj.photos:
            link = '<img src="%s" height="250"/>' % photo.image.url
            p.append(link)
        return mark_safe(','.join(p))


class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'rate', 'start_on', 'end_on')
    search_fields = ('code',)


site.register(BundleType, BundleTypeAdmin)
site.register(Bundle, BundleAdmin)
site.register(PromoCode, PromoCodeAdmin)
site.register(ComCampaign, ComCampaignAdmin)