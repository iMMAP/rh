# from django.test import TestCase, Client
# from django.contrib.auth.models import User
# from django.urls import reverse
# from rh.models import *
# from rh.views import *

# class TestLoggedInViews(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='testpassword')
#         self.client.login(username='testuser', password='testpassword')

#         self.index_url = reverse('index')
#         self.home_url = reverse('home')
#         self.load_locations_details_url = reverse('ajax-load-districts')
#         self.load_facility_sites_url = reverse('ajax-load-facility_sites')

#     def test_index_view(self):
#         # Create dummy data
#         User.objects.create(username='user1')
#         Location.objects.create(name='location1', parent=None)

#         response = self.client.get(self.index_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'index.html')
#         self.assertContains(response, 'Users')
#         self.assertContains(response, 'Locations')
#         self.assertContains(response, User.objects.all().count())
#         self.assertContains(response, Location.objects.all().count())
#         print('Logged In. Welcome Index Page. Test for index view (authenticated user) passed.')

#     def test_home_view(self):
#         # Create dummy data
#         Location.objects.create(name='location1', parent=None)

#         response = self.client.get(self.home_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'home.html')
#         self.assertContains(response, 'Users')
#         self.assertContains(response, 'Locations')
#         self.assertContains(response, User.objects.all().count())
#         self.assertContains(response, Location.objects.all().count())
#         print('Logged In! Welcome to Home Page. Test for home view (authenticated user) passed.')

#     def test_load_locations_details_view(self):
#         # Create dummy provinces and districts
#         province1 = Location.objects.create(name='Province 1', parent=None)
#         district1 = Location.objects.create(name='District 1', parent=province1)
#         district2 = Location.objects.create(name='District 2', parent=province1)

#         province2 = Location.objects.create(name='Province 2', parent=None)
#         district3 = Location.objects.create(name='District 3', parent=province2)
#         district4 = Location.objects.create(name='District 4', parent=province2)

#         # Prepare GET request parameters
#         params = {
#             'provinces[]': [str(province1.pk), str(province2.pk)],
#             'listed_districts[]': []
#         }

#         response = self.client.get(self.load_locations_details_url, params)

#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, f'<optgroup label="{province1.name}">')
#         self.assertContains(response, f'<option value="{district1.pk}">{district1}</option>')
#         self.assertContains(response, f'<option value="{district2.pk}">{district2}</option>')
#         self.assertContains(response, f'<optgroup label="{province2.name}">')
#         self.assertContains(response, f'<option value="{district3.pk}">{district3}</option>')
#         self.assertContains(response, f'<option value="{district4.pk}">{district4}</option>')

#         print('Test for load_locations_details view passed.')

#     def test_load_facility_sites_view(self):
#         # Create dummy clusters and facility sites
#         cluster1 = Cluster.objects.create(name='Cluster 1')
#         facility1 = FacilitySiteType.objects.create(name='Facility 1', cluster=cluster1)
#         facility2 = FacilitySiteType.objects.create(name='Facility 2', cluster=cluster1)

#         cluster2 = Cluster.objects.create(name='Cluster 2')
#         facility3 = FacilitySiteType.objects.create(name='Facility 3', cluster=cluster2)
#         facility4 = FacilitySiteType.objects.create(name='Facility 4', cluster=cluster2)

#         # Prepare GET request parameters
#         params = {
#             'clusters[]': [str(cluster1.pk), str(cluster2.pk)],
#             'listed_facilities[]': []
#         }

#         response = self.client.get(self.load_facility_sites_url, params)

#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, f'<optgroup label="{cluster1.name}">')
#         self.assertContains(response, f'<option value="{facility1.pk}">{facility1}</option>')
#         self.assertContains(response, f'<option value="{facility2.pk}">{facility2}</option>')
#         self.assertContains(response, f'<optgroup label="{cluster2.name}">')
#         self.assertContains(response, f'<option value="{facility3.pk}">{facility3}</option>')
#         self.assertContains(response, f'<option value="{facility4.pk}">{facility4}</option>')

#         print('Test for load_facility_sites view passed.')


# class TestNotLoggedInViews(TestCase):

#     def setUp(self):
#         self.client = Client()
#         self.index_url = reverse('index')
#         self.home_url = reverse('home')
#         self.load_locations_details_url = reverse('ajax-load-districts')
#         self.load_facility_sites_url = reverse('ajax-load-facility_sites')


#     def test_index_view(self):
#         # Create dummy data
#         User.objects.create(username='user1')
#         Location.objects.create(name='location1', parent=None)

#         response = self.client.get(self.index_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'index.html')
#         self.assertContains(response, 'Users')
#         self.assertContains(response, 'Locations')
#         self.assertContains(response, User.objects.all().count())
#         self.assertContains(response, Location.objects.all().count())
#         print('Logged In! Welcome to Index Page. Test for index view (unauthenticated user) passed.')

#     def test_home_view(self):
#         # Create dummy data
#         Location.objects.create(name='location1', parent=None)

#         response = self.client.get(self.home_url)
#         self.assertEqual(response.status_code, 302)
#         print('Access Denied! Please login and try again. Test for home view (unauthenticated user) passed.')

#     def test_load_locations_details_view(self):
#         # Create dummy provinces and districts
#         province1 = Location.objects.create(name='Province 1', parent=None)
#         province2 = Location.objects.create(name='Province 2', parent=None)

#         # Prepare GET request parameters
#         params = {
#             'provinces[]': [str(province1.pk), str(province2.pk)],
#             'listed_districts[]': []
#         }

#         response = self.client.get(self.load_locations_details_url, params)

#         self.assertEqual(response.status_code, 302)
#         print('Access Denied! Please login and try again. Test for load_locations_details view passed.')

#     def test_load_facility_sites_view(self):
#         # Create dummy clusters and facility sites
#         cluster1 = Cluster.objects.create(name='Cluster 1')
#         cluster2 = Cluster.objects.create(name='Cluster 2')

#         # Prepare GET request parameters
#         params = {
#             'clusters[]': [str(cluster1.pk), str(cluster2.pk)],
#             'listed_facilities[]': []
#         }

#         response = self.client.get(self.load_facility_sites_url, params)

#         self.assertEqual(response.status_code, 302)
#         print('Access Denied! Please login and try again. Test for load_facility_sites view passed.')
