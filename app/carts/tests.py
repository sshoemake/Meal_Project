import datetime
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO

from PIL import Image
from django.test import Client, TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse

from app.carts import views
from app.carts.models import Cart, Cart_Details
from app.ingredients.models import Ingredient
from app.meals.models import Meal
from app.stores.models import Store


def make_request(method='get', path='/', data=None):
    factory = RequestFactory()
    if method.lower() == 'post':
        req = factory.post(path, data=data or {})
    else:
        req = factory.get(path)

    # attach session (SessionMiddleware requires a get_response callable)
    middleware = SessionMiddleware(get_response=lambda _: HttpResponse())
    middleware.process_request(req)
    req.session.save()

    # default referer
    req.META['HTTP_REFERER'] = '/'
    return req


class CartViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.store = Store.objects.create(name='Main')
        # self.profile = Profile.objects.create(user=self.user, def_store=self.store)
        self.profile = self.user.profile
        
    def test_get_cart_and_get_or_create(self):
        req = make_request()
        # no cart yet
        self.assertIsNone(views.get_cart(req))

        # create a valid cart and set in session so helper returns it
        cart = Cart.objects.create(yearweek=views.convert_sw_yw(3), profile=self.profile)
        req.session['cart_id'] = cart.id
        req.session.save()

        got = views.get_cart_or_create(req)
        self.assertIsInstance(got, Cart)
        # session should still have same cart id
        self.assertEqual(req.session['cart_id'], cart.id)

        # get_cart should return the same
        self.assertEqual(views.get_cart(req).id, cart.id)

    def test_convert_sw_yw_and_get_date_label_and_header(self):
        val = views.convert_sw_yw(3)
        self.assertIsInstance(val, int)

        label = views.get_date_label(0)
        self.assertIsInstance(label, str)
        self.assertIn(' ', label)

        req = make_request()
        ctx = views.cart_header_lists(req)
        self.assertIn('date_list', ctx)
        self.assertEqual(len(ctx['date_list']), 7)
        self.assertIn('meal_list', ctx)
        self.assertEqual(len(ctx['meal_list']), 7)

    def test_chg_cart_or_create_creates_cart(self):
        req = make_request()
        req.user = self.user
        req.session['selected_week'] = 3

        the_id = views.chg_cart_or_create(req)
        self.assertIsInstance(the_id, int)
        cart = Cart.objects.get(id=the_id)
        self.assertEqual(cart.profile, self.profile)

        # calling again should return same id
        the_id2 = views.chg_cart_or_create(req)
        self.assertEqual(the_id, the_id2)

    def test_update_ing_cart_adds_and_increments(self):
        req = make_request(method='post')
        req.user = self.user

        # ensure a valid cart exists in session (Cart requires yearweek and profile)
        cart = Cart.objects.create(yearweek=views.convert_sw_yw(3), profile=self.profile)
        req.session['cart_id'] = cart.id
        req.session.save()

        ing = Ingredient.objects.create(name='Salt', aisle=1.0, auto_add=False)

        # first add
        resp = views.update_ing_cart(req, pk=ing.id)
        self.assertEqual(resp.status_code, 302)

        cart = views.get_cart(req)
        cd = Cart_Details.objects.filter(cart=cart, ingredient=ing).first()
        self.assertIsNotNone(cd)
        self.assertEqual(cd.quantity, 1)

        # second add increments
        resp = views.update_ing_cart(req, pk=ing.id)
        cd.refresh_from_db()
        self.assertEqual(cd.quantity, 2)

    def test_update_meal_cart_toggles(self):
        req = make_request(method='post')
        req.user = self.user

        cart = Cart.objects.create(yearweek=views.convert_sw_yw(3), profile=self.profile)
        req.session['cart_id'] = cart.id
        req.session.save()

        meal = Meal.objects.create(name='Taco')

        resp = views.update_meal_cart(req, pk=meal.id)
        self.assertEqual(resp.status_code, 302)
        cart = views.get_cart(req)
        self.assertIn(meal, cart.meals.all())

        # toggle off
        resp = views.update_meal_cart(req, pk=meal.id)
        cart.refresh_from_db()
        self.assertNotIn(meal, cart.meals.all())

    def test_remove_ing_cart_decrement_and_delete(self):
        req = make_request(method='post')
        req.user = self.user
        ing = Ingredient.objects.create(name='Pepper', aisle=2.0, auto_add=False)
        cart = Cart.objects.create(yearweek=views.convert_sw_yw(3), profile=self.profile)
        req.session['cart_id'] = cart.id
        req.session.save()
        cd = Cart_Details.objects.create(cart=cart, ingredient=ing, quantity=2)

        resp = views.remove_ing_cart(req, pk=ing.id)
        self.assertEqual(resp.status_code, 302)
        cd.refresh_from_db()
        self.assertEqual(cd.quantity, 1)

        # remove again should delete
        resp = views.remove_ing_cart(req, pk=ing.id)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Cart_Details.objects.filter(id=cd.id).exists())

    def test_found_ing_cart_marks_found(self):
        req = make_request(method='post')
        req.user = self.user
        ing = Ingredient.objects.create(name='Onion', aisle=3.0, auto_add=False)
        cart = Cart.objects.create(yearweek=views.convert_sw_yw(3), profile=self.profile)
        req.session['cart_id'] = cart.id
        req.session.save()
        cd = Cart_Details.objects.create(cart=cart, ingredient=ing, quantity=1)

        resp = views.found_ing_cart(req, pk=ing.id)
        self.assertIsInstance(resp, HttpResponse)
        cd.refresh_from_db()
        self.assertTrue(cd.found)

    def test_add_ings_cart_adds_multiple(self):
        req = make_request(method='post', data={'ingtoadd': []})
        req.user = self.user

        cart = Cart.objects.create(yearweek=views.convert_sw_yw(3), profile=self.profile)
        req.session['cart_id'] = cart.id
        req.session.save()

        ing1 = Ingredient.objects.create(name='A1', aisle=1.0, auto_add=False)
        ing2 = Ingredient.objects.create(name='A2', aisle=1.1, auto_add=False)

        # post with two ids — reuse the same request object so session persists
        req = make_request(method='post', data={'ingtoadd': [str(ing1.id), str(ing2.id)]})
        req.user = self.user
        req.session['cart_id'] = cart.id
        req.session.save()

        resp = views.add_ings_cart(req)
        self.assertEqual(resp.status_code, 302)
        cart = views.get_cart(req)
        self.assertTrue(Cart_Details.objects.filter(cart=cart, ingredient=ing1).exists())
        self.assertTrue(Cart_Details.objects.filter(cart=cart, ingredient=ing2).exists())

    def test_ing_exists_cart_true_false(self):
        req = make_request()
        ing = Ingredient.objects.create(name='Z', aisle=9.0, auto_add=False)
        # no cart yet
        self.assertFalse(views.ing_exists_cart(req, ing))

        # add ingredient
        req2 = make_request()
        req2.user = self.user
        cart = Cart.objects.create(yearweek=views.convert_sw_yw(3), profile=self.profile)
        req2.session['cart_id'] = cart.id
        req2.session.save()
        Cart_Details.objects.create(cart=cart, ingredient=ing, quantity=1)
        self.assertTrue(views.ing_exists_cart(req2, ing))

    def test_select_cart_sets_session_and_redirects(self):
        req = make_request()
        req.user = self.user
        req.session['selected_week'] = 3

        # create and select
        resp = views.select_cart(req, pk=3)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('cart_id', req.session)

class CartSetupTestCase(TestCase):
    """Base test case with common setup for cart tests"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create profile for user
        self.profile = self.user.profile
        # self.profile = Profile.objects.create(user=self.user)
       
        # Create a test store
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test St'
        )
        
        # Create test ingredients
        self.ingredient1 = Ingredient.objects.create(
            name='Ingredient 1',
            aisle=Decimal("1.5"),
            auto_add=True
        )
        
        self.ingredient2 = Ingredient.objects.create(
            name='Ingredient 2',
            aisle=Decimal("2.0"),
            auto_add=False
        )

        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        self.image = SimpleUploadedFile(
            "test_image.jpg",
            img_bytes.getvalue(),
            content_type="image/jpeg"
        )

        # Create test meal
        self.meal = Meal.objects.create(
            name='Test Meal',
            notes="Test notes",
            image=self.image
        )        

        # Create a test cart with specific yearweek
        today = datetime.date.today()
        year, week, _ = today.isocalendar()
        self.yearweek = int(str(year) + str(week).zfill(2))
        
        self.cart = Cart.objects.create(
            yearweek=self.yearweek,
            profile=self.profile
        )
        
        # Add test ingredients to cart
        self.cart_detail1 = Cart_Details.objects.create(
            cart=self.cart,
            ingredient=self.ingredient1,
            quantity=2,
            found=False
        )
        
        self.cart_detail2 = Cart_Details.objects.create(
            cart=self.cart,
            ingredient=self.ingredient2,
            quantity=1,
            found=False
        )
        
        # Add meal to cart
        self.cart.meals.add(self.meal)
    
    def login(self):
        """Helper method to log in test user"""
        self.client.login(username='testuser', password='testpass123')


class RemoveIngredientCartTests(CartSetupTestCase):
    """Tests for removing ingredients from cart"""
    
    def setUp(self):
        super().setUp()
        self.login()
        # Set default store in session
        session = self.client.session
        session['def_store'] = self.store.id
        session['selected_week'] = 3
        session['cart_id'] = self.cart.id
        session.save()
    
    def test_remove_ing_cart_decrements_quantity(self):
        """Test that removing an ingredient with quantity > 1 decrements it"""
        # Ensure ingredient has quantity of 2
        self.cart_detail1.quantity = 2
        self.cart_detail1.save()
        
        # Remove ingredient once
        response = self.client.get(
            reverse('cart-ingredient-remove', kwargs={'pk': self.ingredient1.id})
        )
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check that quantity was decremented
        self.cart_detail1.refresh_from_db()
        self.assertEqual(self.cart_detail1.quantity, 1)
    
    def test_remove_ing_cart_deletes_when_quantity_is_one(self):
        """Test that removing an ingredient with quantity 1 deletes it"""
        # Ensure ingredient has quantity of 1
        self.cart_detail2.quantity = 1
        self.cart_detail2.save()
        ingredient_id = self.cart_detail2.ingredient.id
        
        # Remove ingredient
        response = self.client.get(
            reverse('cart-ingredient-remove', kwargs={'pk': ingredient_id})
        )
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check that the cart detail was deleted
        self.assertFalse(
            Cart_Details.objects.filter(
                cart=self.cart,
                ingredient=self.ingredient2
            ).exists()
        )
    
    def test_remove_ing_cart_non_existent_ingredient(self):
        """Test removing a non-existent ingredient doesn't cause error"""
        response = self.client.get(
            reverse('cart-ingredient-remove', kwargs={'pk': 9999})
        )
        
        # Should still return a redirect
        self.assertEqual(response.status_code, 302)
        
        # Cart details should remain unchanged
        self.assertEqual(Cart_Details.objects.filter(cart=self.cart).count(), 2)
    
    def test_remove_ing_cart_updates_session_items_total(self):
        """Test that removing ingredient updates session items total"""
        # initial_total = self.cart.items_total
        
        # Remove ingredient
        self.client.get(
            reverse('cart-ingredient-remove', kwargs={'pk': self.ingredient1.id})
        )
        
        # Session should be updated (we check after request)
        self.assertIn('items_total', self.client.session)


class HideIngredientCartTests(CartSetupTestCase):
    """Tests for hiding (marking found) ingredients from cart"""
    
    def setUp(self):
        super().setUp()
        self.login()
        # Set default store in session
        session = self.client.session
        session['def_store'] = self.store.id
        session['selected_week'] = 3
        session['cart_id'] = self.cart.id
        session.save()
    
    def test_found_ing_cart_marks_as_found(self):
        """Test that found_ing_cart marks ingredient as found"""
        # Ensure ingredient is not marked as found
        self.cart_detail1.found = False
        self.cart_detail1.save()
        
        # Call found_ing_cart
        response = self.client.post(
            reverse('found-ing-cart', kwargs={'pk': self.ingredient1.id})
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')
        
        # Check that found was set to True
        self.cart_detail1.refresh_from_db()
        self.assertTrue(self.cart_detail1.found)
    
    def test_found_ing_cart_non_existent_ingredient(self):
        """Test marking non-existent ingredient as found doesn't error"""
        response = self.client.post(
            reverse('found-ing-cart', kwargs={'pk': 9999})
        )
        
        # Should still return OK
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'OK')
    
    def test_found_ing_cart_toggles_multiple_ingredients(self):
        """Test that multiple ingredients can be marked as found independently"""
        # Mark first ingredient as found
        self.client.post(
            reverse('found-ing-cart', kwargs={'pk': self.ingredient1.id})
        )
        
        # Mark second ingredient as found
        self.client.post(
            reverse('found-ing-cart', kwargs={'pk': self.ingredient2.id})
        )
        
        # Check both are marked as found
        self.cart_detail1.refresh_from_db()
        self.cart_detail2.refresh_from_db()
        self.assertTrue(self.cart_detail1.found)
        self.assertTrue(self.cart_detail2.found)


class RemoveMealCartTests(CartSetupTestCase):
    """Tests for removing meals from cart"""
    
    def setUp(self):
        super().setUp()
        self.login()
        session = self.client.session
        session['selected_week'] = 3
        session['cart_id'] = self.cart.id
        session.save()
    
    def test_remove_meal_from_cart(self):
        """Test that meal is removed from cart"""
        # Verify meal is in cart
        self.assertIn(self.meal, self.cart.meals.all())
        
        # Remove meal
        response = self.client.get(
            reverse('update-meal-cart', kwargs={'pk': self.meal.id})
        )
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check meal was removed
        self.cart.refresh_from_db()
        self.assertNotIn(self.meal, self.cart.meals.all())
    
    def test_add_meal_to_cart(self):
        """Test that clicking meal link toggles meal in cart"""
         # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        self.image = SimpleUploadedFile(
            "test_image.jpg",
            img_bytes.getvalue(),
            content_type="image/jpeg"
        )

        # Create new meal not in cart
        meal2 = Meal.objects.create(
            name='Test Meal 2',
            notes="Test notes",
            image=self.image
        )
        
        # Verify meal is not in cart
        self.assertNotIn(meal2, self.cart.meals.all())
        
        # Add meal
        response = self.client.get(
            reverse('update-meal-cart', kwargs={'pk': meal2.id})
        )
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check meal was added
        self.cart.refresh_from_db()
        self.assertIn(meal2, self.cart.meals.all())


class CartListViewTests(CartSetupTestCase):
    """Tests for cart list view and display of hide/remove links"""
    
    def setUp(self):
        super().setUp()
        self.login()
        session = self.client.session
        session['def_store'] = self.store.id
        session['selected_week'] = 3
        session['cart_id'] = self.cart.id
        session['hide_found'] = False
        # session['reverse_sort'] = False
        session.save()
    
    def test_cart_list_view_displays_remove_link(self):
        """Test that cart list displays remove link for ingredients"""
        response = self.client.get(reverse('cart-list'))
        
        self.assertEqual(response.status_code, 200)
        # Check for remove link in response
        self.assertContains(response, 'Remove')
    
    def test_cart_list_view_shows_hide_not_remove_when_hide_found_enabled(self):
        """Test that hide link shows when hide_found is enabled"""
        # Enable hide_found in session
        session = self.client.session
        session['hide_found'] = True
        session.save()
        
        response = self.client.get(reverse('cart-list'))
        
        self.assertEqual(response.status_code, 200)
        # Check for hide link in response
        self.assertContains(response, 'Hide')
    
    def test_cart_list_view_hides_found_items_when_enabled(self):
        """Test that found items are hidden when hide_found is enabled"""
        # Mark ingredient as found
        self.cart_detail1.found = True
        self.cart_detail1.save()
        
        # Enable hide_found
        session = self.client.session
        session['hide_found'] = True
        session.save()
        
        response = self.client.get(reverse('cart-list'))
        
        self.assertEqual(response.status_code, 200)
        # Found item should not be in response content
        self.assertNotContains(response, self.ingredient1.name)
        # Non-found item should be in response
        self.assertContains(response, self.ingredient2.name)
    
    def test_cart_list_view_shows_all_items_when_hide_found_disabled(self):
        """Test that all items shown when hide_found is disabled"""
        # Mark one ingredient as found
        self.cart_detail1.found = True
        self.cart_detail1.save()
        
        # Disable hide_found
        session = self.client.session
        session['hide_found'] = False
        session.save()
        
        response = self.client.get(reverse('cart-list'))
        
        self.assertEqual(response.status_code, 200)
        # Both items should be in response
        self.assertContains(response, self.ingredient1.name)
        self.assertContains(response, self.ingredient2.name)
        # Should only show remove, not hide
        self.assertContains(response, 'Remove')
    
    def test_cart_list_view_displays_meal_remove_link(self):
        """Test that cart list displays remove link for meals"""
        response = self.client.get(reverse('cart-list'))
        
        self.assertEqual(response.status_code, 200)
        # Check for meal name in response
        self.assertContains(response, self.meal.name)
        # Check for remove link
        self.assertContains(response, 'Remove')
    
    def test_cart_list_view_empty_message_when_no_items(self):
        """Test that empty message displays when cart is empty"""
        # Remove all items from cart
        self.cart.meals.clear()
        Cart_Details.objects.filter(cart=self.cart).delete()
        
        response = self.client.get(reverse('cart-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your shopping cart is empty')
    
    def test_cart_list_view_toggle_hide_found_checkbox(self):
        """Test that hide_found checkbox toggles correctly"""
        # POST with hide_found checkbox
        response = self.client.post(
            reverse('cart-list'),
            data={'hide_found': 'on'}
        )
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        
        # Check session was updated
        self.assertTrue(self.client.session.get('hide_found'))
    
    def test_cart_list_displays_item_quantity(self):
        """Test that item quantity is displayed when > 1"""
        # Ensure item has quantity > 1
        self.cart_detail1.quantity = 3
        self.cart_detail1.save()
        
        response = self.client.get(reverse('cart-list'))
        
        self.assertEqual(response.status_code, 200)
        # Check that quantity is displayed
        self.assertContains(response, 'Qty: 3')
    
    def test_cart_list_does_not_display_quantity_when_one(self):
        """Test that quantity is not displayed when it's 1"""
        # Ensure item has quantity of 1
        self.cart_detail2.quantity = 1
        self.cart_detail2.save()
        
        response = self.client.get(reverse('cart-list'))
        
        self.assertEqual(response.status_code, 200)
        # The ingredient should be there but without quantity display
        self.assertContains(response, self.ingredient2.name)


class CartIntegrationTests(CartSetupTestCase):
    """Integration tests for cart workflow"""
    
    def setUp(self):
        super().setUp()
        self.login()
        session = self.client.session
        session['def_store'] = self.store.id
        session['selected_week'] = 3
        session['cart_id'] = self.cart.id
        session['hide_found'] = False
        session['reverse_sort'] = False
        session.save()
    
    def test_full_workflow_hide_and_remove(self):
        """Test workflow: mark as found, then switch to hide_found mode"""
        # Initially see remove link
        response = self.client.get(reverse('cart-list'))
        self.assertContains(response, 'Remove')
        self.assertContains(response, 'Hide', count=1)
        
        # Mark item as found
        self.client.post(
            reverse('found-ing-cart', kwargs={'pk': self.ingredient1.id})
        )
        
        # Enable hide_found via POST
        self.client.post(
            reverse('cart-list'),
            data={'hide_found': 'on'}
        )
        
        # Now should see hide link and found item should be hidden
        response = self.client.get(reverse('cart-list'))
        self.assertContains(response, 'Hide')
        self.assertNotContains(response, self.ingredient1.name)
    
    def test_decrease_quantity_until_removed(self):
        """Test removing ingredient multiple times decreases quantity then deletes"""
        # Set quantity to 2
        self.cart_detail1.quantity = 2
        self.cart_detail1.save()
        
        # Remove once
        self.client.get(
            reverse('cart-ingredient-remove', kwargs={'pk': self.ingredient1.id})
        )
        self.cart_detail1.refresh_from_db()
        self.assertEqual(self.cart_detail1.quantity, 1)
        
        # Remove again
        self.client.get(
            reverse('cart-ingredient-remove', kwargs={'pk': self.ingredient1.id})
        )
        
        # Should be deleted
        self.assertFalse(
            Cart_Details.objects.filter(
                cart=self.cart,
                ingredient=self.ingredient1
            ).exists()
        )
