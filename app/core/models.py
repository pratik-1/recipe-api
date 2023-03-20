""" Database models
Create Custom User model to use email instead of name as username as default.
Added to settings.py AUTH_USER_MODEL=profiles_api.UserProfile
docs: topics/auth/customizing/#substituting-a-custom-user-model
"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    return os.path.join("uploads", "recipe", filename)


class UserManager(BaseUserManager):
    """This Manager is required for custom user model to be able to create
    and manage users in django CLI tools.
    Inherited from built-in 'BaseUserManager'
    Expect methods to implement: create_user and create_superuser"""

    # ModelManager: Manages objects in system, implemets:
    #  - custom logic (hash password)
    #  - used by django CLI: create_user, create_superuser
    # BaseUserManager: Base class to manage users

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("User must have an email address.")
        # make email normalised
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # encrypt password
        user.set_password(password)
        user.save(using=self._db)  # standard django's way of saving user to db

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)

        # permissionmixins creates variable in usermodel
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Database model for custom users in the system with email
    instead of name as username field"""

    # AbstractBaseUser: Builtin-authentication feature, doesn't include fields
    # PermissionsMixin: Django permission system, includes fields and methods

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # assign appropriate manager for custom user
    # because custom user model is used, we need to provide model manager
    # to be able to create and manage our custom user model.

    objects = UserManager()

    # field used for authentication
    USERNAME_FIELD = "email"

    def get_full_name(self) -> str:
        """Retrieve full name of user"""
        return self.name

    def get_short_name(self) -> str:
        """Retrieve shot name of user"""
        return self.name

    def __str__(self) -> str:
        """Return string representation of our user"""
        return self.email


class Recipe(models.Model):
    """Recipe object."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField("Tag")
    ingredients = models.ManyToManyField("Ingredient")

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag for filtering recipes."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient for recipes."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
