from django.db import models
from django.contrib.auth.models import User

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class Size(models.Model):
    value = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.value


class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sizes = models.ManyToManyField(Size, blank=True) 
    price = models.DecimalField(max_digits=12, decimal_places=0)
    discount_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_sale_percent(self):
        if self.discount_price and self.price > 0:
            percent = 100 - (self.discount_price / self.price * 100)
            return int(percent)
        return 0


# ✅ ĐỂ NGOÀI (KHÔNG thụt vào)
class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def get_price(self):
        if self.product.discount_price:
            return self.product.discount_price
        return self.product.price

    def total_price(self):
        return self.get_price() * self.quantity
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = (
        ('pending', 'Đang xử lý'),
        ('shipping', 'Đang giao'),
        ('done', 'Đã giao'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order #{self.id}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.product.name