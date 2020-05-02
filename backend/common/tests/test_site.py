from django.contrib.sites.models import Site
from django.test import TestCase


class SiteMigrationTest(TestCase):
    def test_site_exists(self):
        self.assertTrue(Site.objects.filter(id=1).exists())

    def test_site_thesharegame(self):
        site = Site.objects.get(id=1)

        self.assertEqual(site.name, "www.thesharegame.com")
        self.assertEqual(site.domain, "www.thesharegame.com")
