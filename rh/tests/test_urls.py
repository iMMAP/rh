from django.test import SimpleTestCase
from django.urls import reverse, resolve
from rh.views import *
class TestUrls(SimpleTestCase):
    
    def test_index_url_resolves(self):
        url = reverse('index')
        resolver = resolve(url)
        self.assertEqual(resolver.func, index)
        print('Test for index URL resolved successfully.')

    def test_home_url_resolves(self):
        url = reverse('home')
        resolver = resolve(url)
        self.assertEqual(resolver.func, home)
        print('Test for home URL resolved successfully.')
