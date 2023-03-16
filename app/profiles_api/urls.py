from django.urls import path, include

from rest_framework.routers import DefaultRouter

from profiles_api import views

# DefaultRouter used to auto-generate routes(list,CRUD) for each ViewSets
router = DefaultRouter()
router.register("hello-viewset", views.HelloViewSet, basename="hello-viewset")
router.register("profile", views.UserProfileViewSet)  # basename from queryset
router.register("feed", views.UserProfileFeedViewSet)

urlpatterns = [
    path("hello-view/", views.HelloApiView.as_view()),
    path("login/", views.UserLoginApiView.as_view()),
    # include router in app's url list
    path("", include(router.urls)),
]
