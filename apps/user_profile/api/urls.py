from django.urls import path

from . import views

urlpatterns = [
    path("user-profile/me/", views.UserProfileAPIView.as_view(), name="user-profile-me"),
]
