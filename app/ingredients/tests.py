from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from django.contrib.auth.models import User

from app.ingredients.models import Ingredient, Ing_Store
from app.stores.models import Store
from app.meals.models import Meal, Meal_Details
from app.carts.models import Cart, Cart_Details
from app.ingredients.views import JSONResponseMixin
from django.http import JsonResponse
import json


class IngredientsViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        # profile is created by the app signal or factory in project
        self.profile = self.user.profile

        # create a store and default session values
        self.store = Store.objects.create(name="Store1", default=True)

    def test_json_response_mixin(self):
        mix = JSONResponseMixin()
        data = {"ok": True}
        resp = mix.render_to_json_response(data)
        self.assertIsInstance(resp, JsonResponse)
        self.assertEqual(json.loads(resp.content.decode()), data)

    def test_ing_list_view_queryset_and_context(self):
        # create ingredients and mapping to store
        i1 = Ingredient.objects.create(name="A", aisle=1.0, auto_add=True)
        i2 = Ingredient.objects.create(name="B", aisle=2.0, auto_add=False)
        Ing_Store.objects.create(ingredient=i1, store=self.store, aisle=5.5)

        # create cart and a cart detail for i2 to appear in cart_item_list
        cart = Cart.objects.create(yearweek=202201, profile=self.profile)
        Cart_Details.objects.create(cart=cart, ingredient=i2, quantity=1)

        # set session keys
        session = self.client.session
        session["def_store"] = self.store.id
        session["cart_id"] = cart.id
        session.save()

        resp = self.client.get(reverse("ingredients-home"))
        self.assertEqual(resp.status_code, 200)

        # object_list should be present and annotated
        obj_list = resp.context["object_list"]
        self.assertGreaterEqual(len(obj_list), 2)
        # ensure annotation exists on at least one object
        annotated = [getattr(o, "ing_store_aisle", None) for o in obj_list]
        self.assertIn(5.5, [a for a in annotated if a is not None])

        # cart_item_list should include ingredient from cart
        self.assertIn(i2, resp.context["cart_item_list"])

    def test_ingredient_display_context(self):
        ing = Ingredient.objects.create(name="C", aisle=1.0, auto_add=True)
        meal = Meal.objects.create(name="Meal1")
        Meal_Details.objects.create(ingredient=ing, meal=meal, quantity=1)

        resp = self.client.get(reverse("ingredients-detail", kwargs={"pk": ing.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("meals", resp.context)
        self.assertIn(meal, resp.context["meals"])
        self.assertIn("store_aisles", resp.context)

    def test_ing_aisle_update_post_creates_ing_store_entries(self):
        ing = Ingredient.objects.create(name="D", aisle=1.0, auto_add=True)
        store2 = Store.objects.create(name="S2")

        # login required
        self.client.login(username="tester", password="pass")

        url = reverse("ingredients-detail", kwargs={"pk": ing.pk})
        data = {
            "Aisles": ["10.5", ""],
            "Store_ids": [str(store2.id), ""],
            "message": "hi",
        }

        resp = self.client.post(url, data)
        # redirect / json response from form handling
        self.assertIn(resp.status_code, (200, 302))

        # Ing_Store should have been created for store2
        self.assertTrue(Ing_Store.objects.filter(ingredient=ing, store=store2).exists())

    def test_ing_create_update_delete_requires_login_and_works(self):
        # create (login required)
        self.client.login(username="tester", password="pass")
        url = reverse("ingredients-create")
        resp = self.client.post(url, {"name": "NewIng", "aisle": "4.2", "auto_add": True})
        self.assertIn(resp.status_code, (302, 303))
        new = Ingredient.objects.get(name="NewIng")

        # update
        url_up = reverse("ingredients-update", kwargs={"pk": new.pk})
        resp = self.client.post(url_up, {"name": "NewIng2", "aisle": "4.2", "auto_add": False})
        self.assertIn(resp.status_code, (302, 303))
        new.refresh_from_db()
        self.assertEqual(new.name, "NewIng2")

        # delete
        url_del = reverse("ingredients-delete", kwargs={"pk": new.pk})
        resp = self.client.post(url_del)
        self.assertIn(resp.status_code, (302, 303))
        self.assertFalse(Ingredient.objects.filter(pk=new.pk).exists())



class IngredientModelTest(TestCase):
    """Test cases for the Ingredient model"""

    def setUp(self):
        """Create test ingredient instances"""
        self.ingredient1 = Ingredient.objects.create(
            name="Tomato",
            aisle=Decimal("1.5"),
            auto_add=True
        )
        self.ingredient2 = Ingredient.objects.create(
            name="Basil",
            aisle=Decimal("2.0"),
            auto_add=False
        )

    def test_ingredient_creation(self):
        """Test creating an ingredient"""
        self.assertEqual(self.ingredient1.name, "Tomato")
        self.assertEqual(self.ingredient1.aisle, Decimal("1.5"))
        self.assertTrue(self.ingredient1.auto_add)

    def test_ingredient_string_representation(self):
        """Test the string representation of an ingredient"""
        self.assertEqual(str(self.ingredient1), "Tomato")

    def test_ingredient_name_is_unique(self):
        """Test that ingredient names are unique"""
        with self.assertRaises(Exception):
            Ingredient.objects.create(
                name="Tomato",
                aisle=Decimal("3.0"),
                auto_add=True
            )

    def test_ingredient_aisle_field_type(self):
        """Test that aisle field properly stores decimal values"""
        self.assertIsInstance(self.ingredient1.aisle, Decimal)
        self.assertEqual(self.ingredient1.aisle, Decimal("1.5"))

    def test_ingredient_auto_add_default(self):
        """Test auto_add boolean field"""
        self.assertTrue(self.ingredient1.auto_add)
        self.assertFalse(self.ingredient2.auto_add)

    def test_ingredient_ordering(self):
        """Test that ingredients are ordered by aisle"""
        ingredients = Ingredient.objects.all()
        self.assertEqual(ingredients[0].aisle, Decimal("1.5"))
        self.assertEqual(ingredients[1].aisle, Decimal("2.0"))

    def test_ingredient_get_absolute_url(self):
        """Test the get_absolute_url method"""
        expected_url = reverse("ingredients-detail", kwargs={"pk": self.ingredient1.pk})
        self.assertEqual(self.ingredient1.get_absolute_url(), expected_url)

    def test_ingredient_max_name_length(self):
        """Test that ingredient name cannot exceed max_length"""
        long_name = "A" * 51  # Exceeds max_length of 50
        ingredient = Ingredient(
            name=long_name,
            aisle=Decimal("5.0"),
            auto_add=True
        )
        with self.assertRaises(Exception):
            ingredient.full_clean()

    def test_ingredient_primary_key(self):
        """Test that ingredient has a BigAutoField primary key"""
        self.assertIsNotNone(self.ingredient1.pk)
        self.assertIsInstance(self.ingredient1.pk, int)

    def test_ingredient_required_fields(self):
        """Test that required fields are enforced"""
        with self.assertRaises(Exception):
            Ingredient.objects.create(
                name="Garlic",
                aisle=Decimal("1.0")
                # Missing auto_add
            )


class IngStoreModelTest(TestCase):
    """Test cases for the Ing_Store model"""

    def setUp(self):
        """Create test instances"""
        self.store = Store.objects.create(
            name="Kroger",
            address="123 Main St",
            city="Atlanta",
            state="GA",
            zip_code="30301",
            default=True
        )
        self.ingredient = Ingredient.objects.create(
            name="Onion",
            aisle=Decimal("3.5"),
            auto_add=True
        )
        self.ing_store = Ing_Store.objects.create(
            ingredient=self.ingredient,
            store=self.store,
            aisle=Decimal("3.5")
        )

    def test_ing_store_creation(self):
        """Test creating an Ing_Store relationship"""
        self.assertEqual(self.ing_store.ingredient, self.ingredient)
        self.assertEqual(self.ing_store.store, self.store)
        self.assertEqual(self.ing_store.aisle, Decimal("3.5"))

    def test_ing_store_foreign_key_to_ingredient(self):
        """Test the foreign key relationship to Ingredient"""
        self.assertIsInstance(self.ing_store.ingredient, Ingredient)
        self.assertEqual(self.ing_store.ingredient.name, "Onion")

    def test_ing_store_foreign_key_to_store(self):
        """Test the foreign key relationship to Store"""
        self.assertIsInstance(self.ing_store.store, Store)
        self.assertEqual(self.ing_store.store.name, "Kroger")

    def test_ing_store_aisle_field_type(self):
        """Test that aisle field properly stores decimal values"""
        self.assertIsInstance(self.ing_store.aisle, Decimal)
        self.assertEqual(self.ing_store.aisle, Decimal("3.5"))

    def test_ing_store_cascade_delete_ingredient(self):
        """Test that Ing_Store is deleted when ingredient is deleted"""
        # ingredient_id = self.ingredient.pk
        ing_store_id = self.ing_store.pk
        
        self.ingredient.delete()
        
        with self.assertRaises(Ing_Store.DoesNotExist):
            Ing_Store.objects.get(pk=ing_store_id)

    def test_ing_store_cascade_delete_store(self):
        """Test that Ing_Store is deleted when store is deleted"""
        ing_store_id = self.ing_store.pk
        
        self.store.delete()
        
        with self.assertRaises(Ing_Store.DoesNotExist):
            Ing_Store.objects.get(pk=ing_store_id)

    def test_multiple_ing_stores_same_ingredient(self):
        """Test that one ingredient can be in multiple stores"""
        store2 = Store.objects.create(
            name="Publix",
            address="456 Oak Ave",
            city="Miami",
            state="FL",
            zip_code="33101"
        )
        Ing_Store.objects.create(
            ingredient=self.ingredient,
            store=store2,
            aisle=Decimal("2.0")
        )
        
        ing_stores = Ing_Store.objects.filter(ingredient=self.ingredient)
        self.assertEqual(ing_stores.count(), 2)

    def test_multiple_ing_stores_same_store(self):
        """Test that one store can have multiple ingredients"""
        ingredient2 = Ingredient.objects.create(
            name="Pepper",
            aisle=Decimal("3.0"),
            auto_add=False
        )
        Ing_Store.objects.create(
            ingredient=ingredient2,
            store=self.store,
            aisle=Decimal("4.0")
        )
        
        ing_stores = Ing_Store.objects.filter(store=self.store)
        self.assertEqual(ing_stores.count(), 2)

    def test_ing_store_primary_key(self):
        """Test that Ing_Store has a BigAutoField primary key"""
        self.assertIsNotNone(self.ing_store.pk)
        self.assertIsInstance(self.ing_store.pk, int)

    def test_ing_store_different_aisle_same_ingredient(self):
        """Test that same ingredient can have different aisles in different stores"""
        store3 = Store.objects.create(
            name="Whole Foods",
            default=False
        )
        ing_store3 = Ing_Store.objects.create(
            ingredient=self.ingredient,
            store=store3,
            aisle=Decimal("5.5")
        )
        
        self.assertEqual(self.ing_store.aisle, Decimal("3.5"))
        self.assertEqual(ing_store3.aisle, Decimal("5.5"))
