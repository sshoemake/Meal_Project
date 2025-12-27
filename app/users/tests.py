from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


# Create your tests here.
class BaseTest(TestCase):
    def setUp(self):
        self.register_url=reverse('register')
        self.login_url=reverse('login')

        self.user={
            'username':'shoes',
            'email':'shoes@shoes.com',
            'password1':'1XISRUkwtuK',
            'password2':'1XISRUkwtuK'
        }
        return super().setUp()
    
class RegisterTest(BaseTest):
    def test_can_view_page_correctly(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_can_register_user(self):
        response = self.client.post(self.register_url,self.user,format='text/html')
        self.assertEqual(response.status_code, 302)
        # self.assertTemplateUsed(response, 'users/register.html')
        # print(response)

    def test_cant_register_duplicate_username(self):
        self.client.post(self.register_url, self.user)

        response = self.client.post(self.register_url, self.user)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that username already exists")


class LoginTest(BaseTest):
    def test_can_access_page(self):
        response=self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_success(self):
        self.client.post(self.register_url,self.user,format='text/html')
        user=User.objects.filter(email=self.user['email']).first()
        user.is_active=True
        user.save()

        response=self.client.post(self.login_url,self.user,format='text/html')
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'users/login.html')
        # print(response)

    def test_cantlogin_with_unverified_email(self):
        # self.client.post(self.register_url,self.user,format='text/html')
        # user=User.objects.filter(email=self.user['email']).first()
        # user.is_active=True
        # user.save()

        response=self.client.post(self.login_url,self.user,format='text/html')
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'users/login.html')
        print(response)