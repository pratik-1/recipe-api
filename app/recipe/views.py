"""View for recipe APIs.
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from . import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View from manage recipe APIs"""

    # All request methods requires 'RecipeDetailSerializer' except list
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]  # allow log-in by token
    permission_classes = [IsAuthenticated]  # checks if logged-in

    def get_queryset(self):
        """Retrieve only recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    # Set serializer_class depending on request
    # https://www.django-rest-framework.org/api-guide/generic-views/#get_serializer_classself
    def get_serializer_class(self):
        if self.action == "list":
            return serializers.RecipeSerializer
        return self.serializer_class

    # overrides object creation to save model in viewset
    # https://www.django-rest-framework.org/api-guide/generic-views/#get_serializer_classself
    def perform_create(self, serializer):
        """Create a new recipe."""
        # On authenticated user save new object after validating data
        serializer.save(user=self.request.user)


class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    # Important: mixins should be imported before GenericViewSet
    authentication_classes = [TokenAuthentication]  # allow log-in by token
    permission_classes = [IsAuthenticated]  # checks if logged-in

    def get_queryset(self):
        """Retrieve only tags for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by("name")


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in database."""

    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in database."""

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
