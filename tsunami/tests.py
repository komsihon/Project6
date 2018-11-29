import json

from django.conf import settings
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.utils import override_settings
from django.utils import unittest
from ikwen.accesscontrol.backends import UMBRELLA

from accesscontrol.tests_auth import wipe_test_data
from tsunami.models import ComCampaign, ComOffer


class TsunamiSetupTestCase(unittest.TestCase):
    """
    This test derives django.utils.unittest.TestCate rather than the default django.test.TestCase.
    Thus, self.client is not automatically created and fixtures not automatically loaded. This
    will be achieved manually by a custom implementation of setUp()
    """
    fixtures = ['bundles.yaml', ]

    def setUp(self):
        self.client = Client()
        for fixture in self.fixtures:
            call_command('loaddata', fixture)
            call_command('loaddata', fixture, database=UMBRELLA)

    def tearDown(self):
        wipe_test_data()
        wipe_test_data(UMBRELLA)

    def test_setup(self):
        call_command('loaddata', 'bundles.yaml', database=UMBRELLA)

    def test_Tsunami_bundles_availability(self):
        """
        Must create a new SmartCategory in the database. SmartObjectList must return HTTP 200 after the operation
        """
        response = self.client.get(reverse('stunami:bundles'))
        self.assertEqual(response.status_code, 200)
        bundles = response.context['bundles']
        self.assertEqual(bundles.count(), 3)

    def test_tsunami_campaign_with_website(self):
        """
        Must create a new SmartCategory in the database. SmartObjectList must return HTTP 200 after the operation
        """
        response = self.client.get(reverse('stunami:bundles'))
        self.assertEqual(response.status_code, 200)
        bundles = response.context['bundles']
        self.assertEqual(bundles.count(), 3)
        self.client.login(username='member4', password='admin')
        response = self.client.post(reverse('billing:momo_set_checkout'),
                                   {
                                    'product_id': '55d1fa8f4464442299bd2251',
                                    'website_needed': True,})
        self.assertEqual(response.status_code, 200)
        campaign = response.context['campaign']
        self.assertEqual(campaign.offer.id, '55d1fa8f4464442299bd2251')
        self.assertEqual(campaign.status, 'Pending')
        response = self.client.post(reverse('tsunami:checkout'),
                                   {
                                    'campaign_id': campaign.id,
                                    'age_range': '20 - 52',
                                    'gender': 'Both',
                                    'location': 'Everywhere',
                                    'network_page_url': 'https://www.facebook.com/ddd/posts/2377664948914065',
                                    'website_needed': True,})
        offer = ComOffer.objects.get(pk='55d1fa8f4464442299bd2251')
        campaign = ComCampaign.objects.filter(offer=offer)[0]
        self.assertEqual(campaign.status, 'Complete')
        self.assertEqual(campaign.cost, 150000)
        self.assertEqual(campaign.website_needed, True)
        self.assertEqual(campaign.has_page, True)

    def test_Tsunami_campaign_without_website(self):
        """
        Must create a new SmartCategory in the database. SmartObjectList must return HTTP 200 after the operation
        """
        response = self.client.get(reverse('stunami:bundles'))
        self.assertEqual(response.status_code, 200)
        bundles = response.context['bundles']
        self.assertEqual(bundles.count(), 3)

    def test_Tsunami_campaign_with_promocode(self):
        """
        Must create a new SmartCategory in the database. SmartObjectList must return HTTP 200 after the operation
        """
        response = self.client.get(reverse('stunami:bundles'))
        self.assertEqual(response.status_code, 200)
        bundles = response.context['bundles']
        self.assertEqual(bundles.count(), 3)
