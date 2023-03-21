"""
Tests for the tags API.
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


def create_user(email="test@example.com", password="test123"):
    """Create and return a user."""
    return get_user_model().objects.create(email=email, password=password)


def create_tag(name="English", user=None):
    """Create and return tag."""
    return Tag.objects.create(name=name, user=user)


def detail_url(tag_id):
    """Return tag detail url."""
    return reverse("recipe:tag-detail", args=[tag_id])


class PublicTestTagsAPi(TestCase):
    """Test unauthenticated Tags API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call tags API."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="test123")
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        create_tag(user=self.user)
        create_tag(user=self.user, name="Italian")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("name")
        serializer = TagSerializer(tags, many=True)  # many return list
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_list_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        other_user = create_user(email="other@example.com", password="test123")
        create_tag(user=other_user)
        tag = create_tag(user=self.user, name="Italian")

        res = self.client.get(TAGS_URL)

        # tags = Tag.objects.filter(user=self.user)  # authenticated user
        # serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag(self):
        """Test update of tag."""
        tag = create_tag(user=self.user)

        payload = {"name": "Indian"}
        url = detail_url(tag.id)

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload["name"])
        self.assertEqual(tag.user, self.user)

    def test_delete_tag(self):
        """Test deleting a tag successful."""
        tag = create_tag(user=self.user)

        url = detail_url(tag.id)
        res = self.client.delete(url)

        # 204 standard http response to delete
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_filter_tags_assigned_to_recipes(self):
        """Test listing tags that are assigned to recipes."""
        tag1 = create_tag(user=self.user, name="Breakfast")
        tag2 = create_tag(user=self.user, name="Lunch")
        recipe = Recipe.objects.create(
            title="Green Eggs on Toast",
            time_minutes=10,
            price=Decimal("2.50"),
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_tags_unique(self):
        """Test filtered tags returns a unique list."""
        tag = create_tag(user=self.user, name="Breakfast")
        create_tag(user=self.user, name="Dinner")
        recipe1 = Recipe.objects.create(
            title="Pancakes",
            time_minutes=5,
            price=Decimal("5.00"),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title="Porridge",
            time_minutes=3,
            price=Decimal("2.00"),
            user=self.user,
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
