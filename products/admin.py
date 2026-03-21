from django.contrib import admin
from .models import Product, Category, Brand, Cart, CartItem, Size, Order, OrderItem

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Size)

# 🔥 thêm cái này
admin.site.register(Order)
admin.site.register(OrderItem)