"""
Tests for the ingredients API.
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse("recipe:ingredient-list")


def create_user(email="test@example.com", password="test123"):
    """Create and return a user."""
    return get_user_model().objects.create(email=email, password=password)


def create_ingredient(name="Tomato", user=None):
    """Create and return ingredient."""
    return Ingredient.objects.create(name=name, user=user)


def detail_url(ingredient_id):
    """Return ingredient detail url."""
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


class PublicTestIngredientsAPi(TestCase):
    """Test unauthenticated Ingredients API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call ingredients API."""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="test123")
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        create_ingredient(user=self.user)
        create_ingredient(user=self.user, name="Vanialla")

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by("name")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_list_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user."""
        other_user = create_user(email="other@example.com", password="test123")
        create_ingredient(user=other_user)
        ingredient = create_ingredient(user=self.user, name="Vanialla")

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)

    def test_update_ingredient(self):
        """Test update of ingredient."""
        # tomato ingredient
        ingredient = create_ingredient(user=self.user)

        # update to vanilla
        payload = {"name": "Butternut squash"}
        url = detail_url(ingredient.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])
        self.assertEqual(ingredient.user, self.user)

    def test_delete_ingredient(self):
        """Test deleting a ingredient successful."""
        ingredient = create_ingredient(user=self.user)

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        # 204 standard http response to delete
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingedients that are assigned to recipes."""
        # create ingredients and assign only few to a recipe
        in1 = create_ingredient(user=self.user, name="Apples")
        in2 = create_ingredient(user=self.user, name="Turkey")
        recipe = Recipe.objects.create(
            title="Apple Crumble",
            time_minutes=5,
            price=Decimal("4.50"),
            user=self.user,
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENT_URL, {"assigned_only": 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        # in2 is not assigned to recipe hence not returned on filter
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""
        ing = create_ingredient(user=self.user, name="Eggs")
        create_ingredient(user=self.user, name="Lentils")
        recipe1 = Recipe.objects.create(
            title="Eggs Benedict",
            time_minutes=60,
            price=Decimal("7.00"),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title="Herb Eggs",
            time_minutes=20,
            price=Decimal("4.00"),
            user=self.user,
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENT_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
