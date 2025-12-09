from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Company(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Company:{self.name}'


class CompanyMember(models.Model):
    user_account = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=50,
        choices=[('Admin', 'Admin'), ('Member', 'Member')]
    )

    def __str__(self):
        return f'Company:{self.company.name}- User: {self.user_account.email}- Role: {self.role}'

    class Meta:
        unique_together = ('user_account', 'company')
