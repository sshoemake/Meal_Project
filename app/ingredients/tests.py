from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from app.ingredients.models import Ingredient, Ing_Store
from app.stores.models import Store


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
        ingredient_id = self.ingredient.pk
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
        ing_store2 = Ing_Store.objects.create(
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
        ing_store2 = Ing_Store.objects.create(
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
