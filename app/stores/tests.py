from django.test import TestCase, Client
from django.urls import reverse

from .models import Store

# Create your tests here.
class TestModels(TestCase):
    def test_model_store(self):
        a_store = Store.objects.create(
            name = 'Test Store',
            address = '1111 test ave',
            city = 'Gilbert',
            state = 'AZ',
            zip_code = '85298'
        )
        self.assertEqual(str(a_store), 'Test Store')
        self.assertTrue(isinstance(a_store, Store))

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

        # urls
        self.listview_url = reverse('store-create')

    def test_listview_GET(self):
        # mock the response
        response = self.client.get(self.listview_url)

        print("debug: ")
        print(response)

        # write assertions