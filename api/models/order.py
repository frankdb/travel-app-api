from django.db import models

from api.models.user import CustomUser


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    email = models.EmailField()
    stripe_session_id = models.CharField(max_length=200)
    payment_status = models.CharField(
        max_length=20, choices=Status.choices, default="pending"
    )
    amount_total = models.DecimalField(max_digits=10, decimal_places=2)
    items = models.JSONField()  # Stores line items from Stripe
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.payment_status}"
