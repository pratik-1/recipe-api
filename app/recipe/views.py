"""View for recipe APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
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
        # Save new object after validating and on authenticated user
        serializer.save(user=self.request.user)
