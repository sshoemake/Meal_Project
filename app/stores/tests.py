from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from app.stores.models import Store, StoreAisleOrder


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


class StoreAisleOrderModelTest(TestCase):
    def setUp(self):
        self.store = Store.objects.create(name="WalkStore")

    def test_order_by_walk_order(self):
        StoreAisleOrder.objects.create(store=self.store, aisle="9.0", walk_order=2)
        StoreAisleOrder.objects.create(store=self.store, aisle="3.0", walk_order=1)
        StoreAisleOrder.objects.create(store=self.store, aisle="6.0", walk_order=3)

        orders = list(StoreAisleOrder.objects.filter(store=self.store))
        self.assertEqual([o.aisle for o in orders], [3, 9, 6])
        self.assertEqual([o.walk_order for o in orders], [1, 2, 3])

    def test_unique_aisle_per_store(self):
        StoreAisleOrder.objects.create(store=self.store, aisle="5.0", walk_order=1)
        with self.assertRaises(IntegrityError):
            StoreAisleOrder.objects.create(store=self.store, aisle="5.0", walk_order=2)

    def test_unique_walk_order_per_store(self):
        StoreAisleOrder.objects.create(store=self.store, aisle="5.0", walk_order=1)
        with self.assertRaises(IntegrityError):
            StoreAisleOrder.objects.create(store=self.store, aisle="7.0", walk_order=1)

    def test_same_aisle_allowed_across_stores(self):
        store2 = Store.objects.create(name="OtherStore")
        StoreAisleOrder.objects.create(store=self.store, aisle="5.0", walk_order=1)
        StoreAisleOrder.objects.create(store=store2, aisle="5.0", walk_order=1)


class StoreUpdateFormSetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        self.store = Store.objects.create(name="CustomStore")
        self.client.login(username="tester", password="pass")

    def _formset_data(self):
        return {
            "aisle_orders-TOTAL_FORMS": "2",
            "aisle_orders-INITIAL_FORMS": "0",
            "aisle_orders-MIN_NUM_FORMS": "0",
            "aisle_orders-MAX_NUM_FORMS": "1000",
            "aisle_orders-0-aisle": "7.0",
            "aisle_orders-0-walk_order": "1",
            "aisle_orders-0-id": "",
            "aisle_orders-1-aisle": "10.5",
            "aisle_orders-1-walk_order": "2",
            "aisle_orders-1-id": "",
        }

    def test_store_update_saves_aisle_order_rows(self):
        url = reverse("store-update", kwargs={"pk": self.store.pk})
        data = {
            "name": self.store.name,
            "address": "",
            "city": "",
            "state": "",
            "zip_code": "",
            "walk_mode": Store.WALK_CUSTOM,
            **self._formset_data(),
        }

        resp = self.client.post(url, data)
        self.assertIn(resp.status_code, (302, 303))

        orders = list(self.store.aisle_orders.order_by("walk_order"))
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0].aisle, 7)
        self.assertEqual(orders[0].walk_order, 1)
        self.assertEqual(orders[1].aisle, 10.5)
        self.assertEqual(orders[1].walk_order, 2)

    def test_store_update_without_formset_data_saves_no_rows(self):
        url = reverse("store-update", kwargs={"pk": self.store.pk})
        data = {
            "name": self.store.name,
            "address": "",
            "city": "",
            "state": "",
            "zip_code": "",
            "walk_mode": Store.WALK_CUSTOM,
        }

        resp = self.client.post(url, data)
        self.assertIn(resp.status_code, (302, 303))
        self.assertFalse(self.store.aisle_orders.exists())
