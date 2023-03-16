"""
Create Custom User model to use email instead of name as username as default.
Added to settings.py AUTH_USER_MODEL=profiles_api.UserProfile
docs: topics/auth/customizing/#substituting-a-custom-user-model
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.conf import settings


class UserProfileManager(BaseUserManager):
    """This Manager is required for custom user model to be able to create
    and manage users in django CLI tools.
    Inherited from built-in 'BaseUserManager'
    Expected methods: create_user and create_superuser"""

    def create_user(self, email, name, password=None) -> BaseUserManager:
        """Create a new user profile"""
        if not email:
            raise ValueError("User must have an email address")

        email = self.normalize_email(email)  # make input lower,caseinsensitive
        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)  # standard django's way of saving user to db

        return user

    def create_superuser(self, email, name, password) -> BaseUserManager:
        """Create and save a new superuser with given details"""
        user = self.create_user(email, name, password)

        # permissionmixins creates variable in usermodel
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database model for custom users in the system with email
    instead of name as username field"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # because custom user model is used, we need to provide model manager
    # to be able to create and manage our custom user model.
    objects = UserProfileManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]  # additional required field

    def get_full_name(self) -> str:
        """Retrieve full name of user"""
        return self.name

    def get_short_name(self) -> str:
        """Retrieve shot name of user"""
        return self.name

    def __str__(self) -> str:
        """Return string representation of our user"""
        return self.email


class ProfileFeedItem(models.Model):
    """Profile status update"""

    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL,
                                     on_delete=models.CASCADE)
    status_text = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return the model as a string"""
        return self.status_text
