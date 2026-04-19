from django.db import models
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Chờ thanh toán'),
        ('Processing', 'Đang xử lý'),
        ('Completed', 'Đã thanh toán'),
        ('Cancelled', 'Đã hủy'),
    )
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_method = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=12, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    # Thêm dòng này:
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10)