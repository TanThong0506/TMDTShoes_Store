from django.db import models
from products.models import Product

class Order(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    payment_method = models.CharField(max_length=20)
    total_price = models.DecimalField(max_digits=12, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    # THÊM: Trạng thái đơn hàng (để template không bị trống tag badge)
    status = models.CharField(max_length=20, default='Chờ xử lý')

    def __str__(self):
        return f"Order {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10)

    # THÊM: Hàm tính tổng tiền cho từng dòng sản phẩm
    def get_cost(self):
        return self.price * self.quantity