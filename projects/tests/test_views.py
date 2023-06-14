from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import *
from projects.views import *

class TestLoggedInViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.index_url = reverse('index')
        self.home_url = reverse('home')
        self.load_locations_details_url = reverse('ajax-load-districts')
        self.load_facility_sites_url = reverse('ajax-load-facility_sites')

    def test_load_facility_sites_view(self):
        # Create dummy clusters and facility sites
        cluster1 = Cluster.objects.create(name='Cluster 1')
        facility1 = FacilitySiteType.objects.create(name='Facility 1', cluster=cluster1)
        facility2 = FacilitySiteType.objects.create(name='Facility 2', cluster=cluster1)

        cluster2 = Cluster.objects.create(name='Cluster 2')
        facility3 = FacilitySiteType.objects.create(name='Facility 3', cluster=cluster2)
        facility4 = FacilitySiteType.objects.create(name='Facility 4', cluster=cluster2)

        # Prepare GET request parameters
        params = {
            'clusters[]': [str(cluster1.pk), str(cluster2.pk)],
            'listed_facilities[]': []
        }

        response = self.client.get(self.load_facility_sites_url, params)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<optgroup label="{cluster1.name}">')
        self.assertContains(response, f'<option value="{facility1.pk}">{facility1}</option>')
        self.assertContains(response, f'<option value="{facility2.pk}">{facility2}</option>')
        self.assertContains(response, f'<optgroup label="{cluster2.name}">')
        self.assertContains(response, f'<option value="{facility3.pk}">{facility3}</option>')
        self.assertContains(response, f'<option value="{facility4.pk}">{facility4}</option>')

        print('Test for load_facility_sites view passed.')


class TestNotLoggedInViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')
        self.home_url = reverse('home')
        self.load_locations_details_url = reverse('ajax-load-districts')
        self.load_facility_sites_url = reverse('ajax-load-facility_sites')


    def test_load_facility_sites_view(self):
        # Create dummy clusters and facility sites
        cluster1 = Cluster.objects.create(name='Cluster 1')
        cluster2 = Cluster.objects.create(name='Cluster 2')

        # Prepare GET request parameters
        params = {
            'clusters[]': [str(cluster1.pk), str(cluster2.pk)],
            'listed_facilities[]': []
        }

        response = self.client.get(self.load_facility_sites_url, params)

        self.assertEqual(response.status_code, 302)
        print('Access Denied! Please login and try again. Test for load_facility_sites view passed.')
