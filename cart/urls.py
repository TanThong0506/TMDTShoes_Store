from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # Sửa 2 dòng dưới này từ int thành str:
    path('update/<str:item_key>/<str:action>/', views.update_cart, name='update_cart'),
    path('remove/<str:item_key>/', views.remove_from_cart, name='remove_from_cart'),
    
    # THÊM DÒNG NÀY VÀO:
    path('checkout/', views.checkout, name='checkout'),
]