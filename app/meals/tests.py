from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from io import BytesIO
from app.meals.models import Meal, Meal_Details
from app.ingredients.models import Ingredient


class MealModelTest(TestCase):
    """Test cases for the Meal model"""

    def setUp(self):
        """Create test meal instances"""
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
        
        self.meal1 = Meal.objects.create(
            name="Spaghetti",
            notes="Classic Italian pasta",
            image=self.image
        )

    def test_meal_creation(self):
        """Test creating a meal"""
        self.assertEqual(self.meal1.name, "Spaghetti")
        self.assertEqual(self.meal1.notes, "Classic Italian pasta")

    def test_meal_string_representation(self):
        """Test the string representation of a meal"""
        self.assertEqual(str(self.meal1), "Spaghetti")

    def test_meal_name_is_unique(self):
        """Test that meal names are unique"""
        with self.assertRaises(Exception):
            Meal.objects.create(
                name="Spaghetti",
                notes="Different notes",
                image=self.image
            )

    def test_meal_notes_optional(self):
        """Test that notes field is optional"""
        meal = Meal.objects.create(
            name="Pizza",
            image=self.image
        )
        self.assertIsNone(meal.notes)

    def test_meal_default_image(self):
        """Test default image is set"""
        meal = Meal.objects.create(
            name="Salad"
        )
        self.assertEqual(meal.image.name, "default.jpg")

    def test_meal_image_upload_to_folder(self):
        """Test that images are uploaded to meal_pics folder"""
        self.assertIn("meal_pics", self.meal1.image.name)

    def test_meal_get_absolute_url(self):
        """Test the get_absolute_url method"""
        expected_url = reverse("meal-detail", kwargs={"pk": self.meal1.pk})
        self.assertEqual(self.meal1.get_absolute_url(), expected_url)

    def test_meal_primary_key(self):
        """Test that meal has a BigAutoField primary key"""
        self.assertIsNotNone(self.meal1.pk)
        self.assertIsInstance(self.meal1.pk, int)

    def test_meal_max_name_length(self):
        """Test that meal name cannot exceed max_length"""
        long_name = "A" * 51  # Exceeds max_length of 50
        meal = Meal(name=long_name, image=self.image)
        with self.assertRaises(Exception):
            meal.full_clean()

    def test_meal_image_resize_large(self):
        """Test that large images are resized to 300x300"""
        # Create a large test image
        large_img = Image.new('RGB', (500, 500), color='blue')
        large_img_bytes = BytesIO()
        large_img.save(large_img_bytes, format='JPEG')
        large_img_bytes.seek(0)
        
        large_image = SimpleUploadedFile(
            "large_test_image.jpg",
            large_img_bytes.getvalue(),
            content_type="image/jpeg"
        )
        
        meal = Meal.objects.create(
            name="Large Pizza",
            image=large_image
        )
        
        # Verify image was saved and resized
        self.assertIsNotNone(meal.image)

    def test_meal_image_resize_small(self):
        """Test that small images are not resized"""
        small_img = Image.new('RGB', (100, 100), color='green')
        small_img_bytes = BytesIO()
        small_img.save(small_img_bytes, format='JPEG')
        small_img_bytes.seek(0)
        
        small_image = SimpleUploadedFile(
            "small_test_image.jpg",
            small_img_bytes.getvalue(),
            content_type="image/jpeg"
        )
        
        meal = Meal.objects.create(
            name="Small Snack",
            image=small_image
        )
        
        self.assertIsNotNone(meal.image)

    def test_meal_required_name_field(self):
        meal = Meal(image=self.image)

        with self.assertRaises(ValidationError):
            meal.full_clean()


class MealDetailsModelTest(TestCase):
    """Test cases for the Meal_Details model"""

    def setUp(self):
        """Create test instances"""
        # Create test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        image = SimpleUploadedFile(
            "test_image.jpg",
            img_bytes.getvalue(),
            content_type="image/jpeg"
        )
        
        self.meal = Meal.objects.create(
            name="Pasta Carbonara",
            notes="Traditional Italian dish",
            image=image
        )
        
        self.ingredient1 = Ingredient.objects.create(
            name="Spaghetti",
            aisle=1.0,
            auto_add=True
        )
        
        self.ingredient2 = Ingredient.objects.create(
            name="Eggs",
            aisle=3.0,
            auto_add=True
        )
        
        self.meal_details = Meal_Details.objects.create(
            ingredient=self.ingredient1,
            meal=self.meal,
            quantity=200
        )

    def test_meal_details_creation(self):
        """Test creating meal details"""
        self.assertEqual(self.meal_details.ingredient, self.ingredient1)
        self.assertEqual(self.meal_details.meal, self.meal)
        self.assertEqual(self.meal_details.quantity, 200)

    def test_meal_details_foreign_key_to_ingredient(self):
        """Test the foreign key relationship to Ingredient"""
        self.assertIsInstance(self.meal_details.ingredient, Ingredient)
        self.assertEqual(self.meal_details.ingredient.name, "Spaghetti")

    def test_meal_details_foreign_key_to_meal(self):
        """Test the foreign key relationship to Meal"""
        self.assertIsInstance(self.meal_details.meal, Meal)
        self.assertEqual(self.meal_details.meal.name, "Pasta Carbonara")

    def test_meal_details_quantity_positive(self):
        """Test that quantity is a positive small integer"""
        self.assertGreater(self.meal_details.quantity, 0)
        self.assertIsInstance(self.meal_details.quantity, int)

    def test_meal_details_quantity_max_value(self):
        """Test PositiveSmallIntegerField max value (32767)"""
        meal_details = Meal_Details.objects.create(
            ingredient=self.ingredient1,
            meal=self.meal,
            quantity=32767
        )
        self.assertEqual(meal_details.quantity, 32767)

    def test_meal_details_cascade_delete_ingredient(self):
        """Test that Meal_Details is deleted when ingredient is deleted"""
        meal_details_id = self.meal_details.pk
        self.ingredient1.delete()
        
        with self.assertRaises(Meal_Details.DoesNotExist):
            Meal_Details.objects.get(pk=meal_details_id)

    def test_meal_details_cascade_delete_meal(self):
        """Test that Meal_Details is deleted when meal is deleted"""
        meal_details_id = self.meal_details.pk
        self.meal.delete()
        
        with self.assertRaises(Meal_Details.DoesNotExist):
            Meal_Details.objects.get(pk=meal_details_id)

    def test_multiple_meal_details_same_meal(self):
        """Test that a meal can have multiple ingredients"""
        meal_details2 = Meal_Details.objects.create(
            ingredient=self.ingredient2,
            meal=self.meal,
            quantity=150
        )
        
        meal_details = Meal_Details.objects.filter(meal=self.meal)
        self.assertEqual(meal_details.count(), 2)

    def test_multiple_meal_details_same_ingredient(self):
        """Test that an ingredient can be in multiple meals"""
        # Create another meal
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        image = SimpleUploadedFile(
            "test_image2.jpg",
            img_bytes.getvalue(),
            content_type="image/jpeg"
        )
        
        meal2 = Meal.objects.create(
            name="Lasagna",
            image=image
        )
        
        meal_details2 = Meal_Details.objects.create(
            ingredient=self.ingredient1,
            meal=meal2,
            quantity=300
        )
        
        meal_details = Meal_Details.objects.filter(ingredient=self.ingredient1)
        self.assertEqual(meal_details.count(), 2)

    def test_meal_details_ordering_by_ingredient_aisle(self):
        """Test that meal details are ordered by ingredient aisle"""
        # ingredient1 has aisle 1.0, ingredient2 has aisle 3.0
        meal_details2 = Meal_Details.objects.create(
            ingredient=self.ingredient2,
            meal=self.meal,
            quantity=150
        )
        
        meal_details_list = Meal_Details.objects.filter(meal=self.meal)
        self.assertEqual(meal_details_list[0].ingredient.aisle, 1.0)
        self.assertEqual(meal_details_list[1].ingredient.aisle, 3.0)

    def test_meal_details_primary_key(self):
        """Test that Meal_Details has a BigAutoField primary key"""
        self.assertIsNotNone(self.meal_details.pk)
        self.assertIsInstance(self.meal_details.pk, int)

    def test_meal_details_different_quantities(self):
        """Test that same ingredient can have different quantities in different meals"""
        img = Image.new('RGB', (100, 100), color='green')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        image = SimpleUploadedFile(
            "test_image3.jpg",
            img_bytes.getvalue(),
            content_type="image/jpeg"
        )
        
        meal2 = Meal.objects.create(
            name="Fettuccine",
            image=image
        )
        
        meal_details2 = Meal_Details.objects.create(
            ingredient=self.ingredient1,
            meal=meal2,
            quantity=400
        )
        
        self.assertEqual(self.meal_details.quantity, 200)
        self.assertEqual(meal_details2.quantity, 400)
