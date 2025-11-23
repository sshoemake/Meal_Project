from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from app.users.models import Profile
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

        a_store = Store.objects.create(
            name = 'Test Store',
            address = '1111 test ave',
            city = 'Gilbert',
            state = 'AZ',
            zip_code = '85298',
            default=True
        )

        self.the_user = User.objects.create(username='user',password='1XISRUkwtuK')
        # the_user.save()

        # profile = Profile.objects.create(user=self.the_user, def_store=a_store) 
        # # user(Profile=profile)
        # self.client.login(username='user',password='1XISRUkwtuK')

        self.user={
            'username':'shoes',
            'email':'sshoemake@yahoo.com',
            'password1':'1XISRUkwtuK',
            'password2':'1XISRUkwtuK'
        }

        self.register_url=reverse('register')
        self.client.post(self.register_url,self.user,format='text/html')
        user=User.objects.filter(email=self.user['email']).first()
        user.is_active=True
        user.profile.def_store = a_store
        user.save()

        self.client.login(username='shoes',password='1XISRUkwtuK')


        # urls
        self.listview_url = reverse('store-create')

    def test_listview_GET(self):
        # mock the response
        response = self.client.get(self.listview_url)

        print(f'test_listview_GET {response}')

        # write assertions