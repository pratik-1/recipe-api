from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework import filters
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated

from profiles_api import serializers
from profiles_api import models
from profiles_api import permissions


class HelloApiView(APIView):
    """Test API View"""

    # 'API View' allows to override different http requests like
    # get, post, put, patch, delete

    serializer_class = serializers.HelloSerializer

    def get(self, request, format=None) -> Response:
        """Returns a list of APIView features"""
        an_apiview = [
            "Uses HTTP methods as function (get, post, patch, put, delete)",
            "Is similar to a traditional Django View",
            "Gives you the most control over you application logic",
            "Is mapped manually to URLs",
        ]

        return Response({"message": "Hello!", "an_apiview": an_apiview})

    def post(self, request) -> Response:
        """Create a hello message with our name"""
        # self.serializer_class is method from APIView to retrieve
        # declared serialiser.Standard way retrieve data in view.
        serializer = self.serializer_class(data=request.data)

        # here check data validation through serialiser
        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            message = f"Hello {name}"
            return Response({"message": message})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None) -> Response:
        """Handle updating an object"""
        return Response({"method": "PUT"})

    def patch(self, request, pk=None) -> Response:
        """Handle a partial update of an object"""
        return Response({"method": "PATCH"})

    def delete(self, request, pk=None) -> Response:
        """Delete an object"""
        return Response({"method": "DELETE"})


class HelloViewSet(viewsets.ViewSet):
    """Test API ViewSet"""

    # ViewSet used to map common API object actions.
    # Uses model/database operations for functions like
    # list, create, retrieve, update, partial_update, destroy

    serializer_class = serializers.HelloSerializer

    def list(self, request) -> Response:
        """Return a hello message"""
        a_viewset = [
            "Uses actions (list, create,retrieve, update, partial_update)",
            "Automatically maps to URLs using Routers",
            "Provides more functionality with less code",
        ]

        return Response({"message": "Hello!", "a_viewset": a_viewset})

    def create(self, request) -> Response:
        """Create a new hello message"""
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            message = f"Hello {name}!"
            return Response({"message": message})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None) -> Response:
        """Handle getting an object by its ID"""
        return Response({"http_method": "GET"})

    def update(self, request, pk=None) -> Response:
        """Handle updating an object"""
        return Response({"http_method": "PUT"})

    def partial_update(self, request, pk=None) -> Response:
        """Handle updating part of an object"""
        return Response({"http_method": "PATCH"})

    def destroy(self, request, pk=None) -> Response:
        """Handle removing an object"""
        return Response({"http_method": "DELETE"})


class UserProfileViewSet(viewsets.ModelViewSet):
    """This Viewset handle creating and updating profiles"""

    # ModelViewSet specifically useful to manage models through APIs.
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfile.objects.all()

    # add authentication layer
    authentication_classes = (TokenAuthentication,)
    # check for permissions/authorisation using declared permissions
    permission_classes = (permissions.UpdateOwnProfile,)
    # allows filters on specific fields
    filter_backends = (filters.SearchFilter,)
    search_fields = (
        "name",
        "email",
    )


class UserLoginApiView(ObtainAuthToken):
    """Handle creating user authentication tokens"""

    # ObtainAuthToken can be added directly to urls.py.
    # However, 'renderer_classes' not available in browsable django admin site.
    # Hence we have to make it available in browsable admin API
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserProfileFeedViewSet(viewsets.ModelViewSet):
    """Handles creating, reading and updating profile feed items"""

    authentication_classes = (TokenAuthentication,)
    serializer_class = serializers.ProfileFeedItemSerializer
    queryset = models.ProfileFeedItem.objects.all()
    permission_classes = (permissions.UpdateOwnStatus, IsAuthenticated)

    # Customise create feed object functionality to limit to
    # only logged-in user using 'perform_create'
    # Without this function overriden,'serializer' calls save method by default
    def perform_create(self, serializer) -> None:
        """Sets the user profile to the logged in user"""
        serializer.save(user_profile=self.request.user)
