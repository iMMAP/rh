from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from rh.models import Cluster, Location, Organization
from users.models import Profile


class TestLoggedInViews(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(username="testuser", password="testpassword")
        org = Organization.objects.create(name="immap", code="immap")
        Profile.objects.create(user=self.user, organization=org)

        self.client.login(username="testuser", password="testpassword")

        self.landing_url = reverse("landing")
        self.load_locations_details_url = reverse("get-locations-details")
        self.load_facility_sites_url = reverse("ajax-load-facility_sites")

    def test_landing_view(self):
        # Create dummy data
        Location.objects.create(name="location1", code="l1", parent=None)

        response = self.client.get(self.landing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        print("Logged In! Welcome to landing Page. Test for landing view (authenticated user) passed.")

    def test_load_locations_details_view(self):
        # Create dummy provinces and districts
        province1 = Location.objects.create(name="Province 1", code="p1", parent=None)

        province2 = Location.objects.create(name="Province 2", code="p2", parent=None)

        # Prepare GET request parameters
        params = {"provinces[]": [str(province1.pk), str(province2.pk)], "listed_districts[]": []}

        response = self.client.get(self.load_locations_details_url, params)

        self.assertEqual(response.status_code, 200)

        print("Test for load_locations_details view passed.")

    def test_load_facility_sites_view(self):
        # Create dummy clusters and facility sites
        cluster1 = Cluster.objects.create(name="Cluster 1", code="c1")

        cluster2 = Cluster.objects.create(name="Cluster 2", code="c2")

        # Prepare GET request parameters
        params = {"clusters[]": [str(cluster1.pk), str(cluster2.pk)], "listed_facilities[]": []}

        response = self.client.get(self.load_facility_sites_url, params)

        self.assertEqual(response.status_code, 200)

        print("Test for load_facility_sites view passed.")


class TestNotLoggedInViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.landing_url = reverse("landing")
        self.load_locations_details_url = reverse("get-locations-details")
        self.load_facility_sites_url = reverse("ajax-load-facility_sites")

    def test_landing_view(self):
        # Create dummy data
        User.objects.create(username="user1")
        Location.objects.create(name="location1", code="l1", parent=None)

        response = self.client.get(self.landing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "landing.html")
        self.assertContains(response, "Users")
        self.assertContains(response, "Locations")
        self.assertContains(response, User.objects.all().count())
        self.assertContains(response, Location.objects.all().count())
        print("Logged In! Welcome to landing Page. Test for landing view (unauthenticated user) passed.")

    def test_load_locations_details_view(self):
        # Create dummy provinces and districts
        province1 = Location.objects.create(name="Province 1", code="p1", parent=None)
        province2 = Location.objects.create(name="Province 2", code="p2", parent=None)

        # Prepare GET request parameters
        params = {"provinces[]": [str(province1.pk), str(province2.pk)], "listed_districts[]": []}

        response = self.client.get(self.load_locations_details_url, params)

        self.assertEqual(response.status_code, 302)
        print("Access Denied! Please login and try again. Test for load_locations_details view passed.")

    def test_load_facility_sites_view(self):
        # Create dummy clusters and facility sites
        cluster1 = Cluster.objects.create(name="Cluster 1", code="c1")
        cluster2 = Cluster.objects.create(name="Cluster 2", code="c2")

        # Prepare GET request parameters
        params = {"clusters[]": [str(cluster1.pk), str(cluster2.pk)], "listed_facilities[]": []}

        response = self.client.get(self.load_facility_sites_url, params)

        self.assertEqual(response.status_code, 302)
        print("Access Denied! Please login and try again. Test for load_facility_sites view passed.")
