from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class QuickBooksCompany(models.Model):
    user_account = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    company_name = models.CharField(max_length=255)
    realm_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class QuickBooksOAuthToken(models.Model):
    company = models.OneToOneField(QuickBooksCompany, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    access_token_expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def is_access_token_valid(self):
        return self.access_token_expires_at > timezone.now()
