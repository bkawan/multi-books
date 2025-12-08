from django.db import models


class Customer(models.Model):
    # Company info
    company_name = models.CharField(max_length=255, blank=False, verbose_name="Company Name")
    sales_tax_id = models.CharField(max_length=255, blank=False, verbose_name="Sales Tax ID")
    customer_id = models.CharField(max_length=255, blank=False, verbose_name="Customer ID")
    license_id = models.CharField(max_length=255, blank=False, verbose_name="License / Permit")
    company_registration_no = models.CharField(max_length=255, blank=True, null=True,
                                               verbose_name="Company Registration No")
    duns = models.CharField(max_length=255, blank=True, null=True, verbose_name="DUNS")
    fincen = models.CharField(max_length=255, blank=True, null=True, verbose_name="FINCEN")
    dba = models.CharField(max_length=255, blank=False, verbose_name="Doing Business As (DBA)")
    tax_id = models.CharField(max_length=255, blank=False, verbose_name="Federal Tax ID (TIN/EIN)")

    # Address
    country = models.CharField(max_length=255, blank=False, verbose_name="Country")
    city = models.CharField(max_length=255, blank=False, verbose_name="City")
    state = models.CharField(max_length=255, blank=False, verbose_name="State")
    street_address = models.CharField(max_length=255, blank=False, verbose_name="Street Address")
    zipcode = models.CharField(max_length=20, blank=True, null=True, verbose_name="Zip Code")

    # Company contact
    company_email1 = models.EmailField(blank=False, verbose_name="Primary Company Email")
    company_email2 = models.EmailField(blank=True, null=True, verbose_name="Secondary Company Email")
    company_contact1 = models.CharField(max_length=50, blank=False, verbose_name="Primary Company Contact")
    company_contact2 = models.CharField(max_length=50, blank=True, null=True, verbose_name="Secondary Company Contact")

    # Customer contact
    customer_email1 = models.EmailField(blank=True, null=True, verbose_name="Primary Customer Email")
    customer_email2 = models.EmailField(blank=True, null=True, verbose_name="Secondary Customer Email")
    customer_contact1 = models.CharField(max_length=50, blank=True, null=True, verbose_name="Primary Customer Contact")
    customer_contact2 = models.CharField(max_length=50, blank=True, null=True,
                                         verbose_name="Secondary Customer Contact")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name
