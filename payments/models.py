from django.db import models

# Create your models here.
from orders.models import Order


class Payment(models.Model):

    PAYMENT_METHODS = [
        ('transfer', 'Transferencia'),
        ('qr', 'QR'),
        ('key', 'Llaves'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago pedido {self.order.id}"