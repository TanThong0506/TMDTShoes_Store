from django.db import models
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Chờ thanh toán'),
        ('Processing', 'Đang xử lý'),
        ('Completed', 'Đã thanh toán/Hoàn thành'),
        ('Return_Requested', 'Yêu cầu đổi/trả'),
        ('Returned', 'Đã đổi/trả'),
        ('Return_Denied', 'Từ chối đổi/trả'),
        ('Cancelled', 'Đã hủy'),
    )
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_method = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=12, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    return_reason = models.TextField(blank=True, null=True, verbose_name="Lý do đổi/trả")

    @property
    def can_return(self):
        from django.utils import timezone
        import datetime
        # Chỉ cho phép đổi trả với đơn hàng Đã giao thành công
        if self.status == 'Completed':
            now = timezone.now()
            return (now - self.created_at) <= datetime.timedelta(days=7)
        return False

    def __str__(self):
        return f"Order #{self.id}"

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10)

    def get_cost(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"