"""
Tests for the tags API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag

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
