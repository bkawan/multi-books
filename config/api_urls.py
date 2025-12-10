from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    # Auth
    path('auth/', include('apps.user_auth.api.urls')),
    path("", include('apps.user_profile.api.urls')),

]
