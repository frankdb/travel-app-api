from rest_framework import serializers

from api.models.order import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "email",
            "payment_status",
            "amount_total",
            "items",
            "created_at",
        ]
