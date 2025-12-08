from django.db import models


class Invoice(models.Model):
    customer_id = models.CharField(max_length=255, blank=False, verbose_name="Customer Id")  # CustomerRef.value
    invoice_no = models.CharField(max_length=255, blank=False, verbose_name="Invoice No")  # DocNumber
    invoice_date = models.DateTimeField(blank=False, verbose_name="Invoice Date")  # TxnDate
    invoice_type = models.CharField(max_length=255, blank=True, null=True, verbose_name="Invoice Type")
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=False, verbose_name="Amount")  # TotalAmt
    invoice_balance = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                          verbose_name="Invoice Balance")  # Balance
    due_date = models.DateField(blank=False, verbose_name="Due Date")  # DueDate
    discount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                   verbose_name="Discount")  # Line.$Index.Amount
    reference = models.CharField(max_length=255, blank=True, null=True, verbose_name="Reference")
    invoice_link = models.CharField(max_length=500, blank=True, null=True, verbose_name="Invoice Link")

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Invoice {self.invoice_no}"
