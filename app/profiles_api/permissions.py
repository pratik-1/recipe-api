from rest_framework import permissions


class UpdateOwnProfile(permissions.BasePermission):
    """Allow user to view all but edit only their own profile"""

    # override has_object_permission method to check if requested user has
    # permissions
    def has_object_permission(self, request, view, obj) -> bool:
        """Check user is trying to edit their own profile"""
        # SAFE_METHODS are methods that don't make changes to the object,
        # eg: GET
        # Allow to 'View' all profiles
        if request.method in permissions.SAFE_METHODS:
            return True
        # else check user is authenticated
        # checking if profile object's id is requested user's id
        return obj.id == request.user.id


class UpdateOwnStatus(permissions.BasePermission):
    """Allow users to update their own status"""

    def has_object_permission(self, request, view, obj) -> bool:
        """Check the user is trying to update their own status"""
        if request.method in permissions.SAFE_METHODS:
            return True

        # check if changes to feed object is owned by requested user
        return obj.user_profile.id == request.user.id
