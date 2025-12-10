from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from . import views

urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="api_login"),
    path("jwt/login/", TokenObtainPairView.as_view(), name="jwt_login"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt_token_refresh"),
    path("token/login/", views.TokenLoginAPIView.as_view(), name="token_login"),
]
