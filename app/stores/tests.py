from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from app.stores.models import Store


class StoreViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")

    def test_store_list_view_shows_stores(self):
        Store.objects.create(name="Alpha")
        Store.objects.create(name="Beta")

        resp = self.client.get(reverse("store-list"))

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Alpha")
        self.assertContains(resp, "Beta")

    def test_store_create_requires_login_and_creates(self):
        url = reverse("store-create")

        # not logged in should redirect
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

        # login and post valid data
        self.client.login(username="tester", password="pass")
        data = {
            "name": "New Store",
            "address": "123 Main",
            "city": "Town",
            "state": "TS",
            "zip_code": "12345",
            "walk_mode": Store.WALK_STANDARD,
        }
        resp = self.client.post(url, data)

        # should redirect after successful create
        self.assertIn(resp.status_code, (302, 303))
        self.assertTrue(Store.objects.filter(name="New Store").exists())

    def test_store_detail_view(self):
        s = Store.objects.create(name="DetailStore")
        resp = self.client.get(reverse("store-detail", kwargs={"pk": s.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "DetailStore")

    def test_store_update_clears_other_defaults(self):
        # create two stores, one default
        s1 = Store.objects.create(name="S1", default=True)
        s2 = Store.objects.create(name="S2", default=False)

        self.client.login(username="tester", password="pass")

        url = reverse("store-update", kwargs={"pk": s2.pk})
        data = {
            "name": s2.name,
            "address": s2.address,
            "city": s2.city,
            "state": s2.state,
            "zip_code": s2.zip_code,
            "default": True,
            "walk_mode": s2.walk_mode,
        }

        resp = self.client.post(url, data)
        self.assertIn(resp.status_code, (302, 303))

        s1.refresh_from_db()
        s2.refresh_from_db()

        self.assertFalse(s1.default)
        self.assertTrue(s2.default)

    def test_store_delete_view(self):
        s = Store.objects.create(name="DelMe")
        self.client.login(username="tester", password="pass")

        url = reverse("store-delete", kwargs={"pk": s.pk})
        resp = self.client.post(url)

        self.assertIn(resp.status_code, (302, 303))
        self.assertFalse(Store.objects.filter(pk=s.pk).exists())

    def test_str_returns_name(self):
        s1 = Store.objects.create(name="Test Name", default=True)
        self.assertEqual(str(s1), "Test Name")