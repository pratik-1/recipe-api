"""
Tests for the ingredients API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient

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
