from django.urls import path
from . import views

app_name = 'orders'  # Dòng này cực kỳ quan trọng

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('create/', views.order_create, name='order_create'),
    path('success/', views.order_success, name='order_success'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('vnpay_return/', views.vnpay_return, name='vnpay_return'),
]