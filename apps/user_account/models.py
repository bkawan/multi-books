# Create your models here.
# Create your models here.

import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.user_account.managers import UserAccountManager


class UserAccount(AbstractUser):
    email = models.EmailField(unique=True, validators=[validate_email])
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    # ------------------------------------------------------------------
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True, unique=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    modified_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # ------------------------------------------------------------------------------
    phone = models.CharField(
        max_length=14,
        unique=True,
        null=True,
        blank=True,
        help_text="Format: 9841-234567"
    )  # ------------------------------------------------------------------------------

    email_is_verified = models.BooleanField(default=False)
    phone_is_verified = models.BooleanField(default=False)

    objects = UserAccountManager()

    def has_usable_password(self):
        return False

    class Meta:
        verbose_name = _('user account')
        verbose_name_plural = _('user accounts')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def company(self):
        from apps.company.models import CompanyMember
        try:
            return self.company_member.company
        except CompanyMember.DoesNotExist:
            return None
