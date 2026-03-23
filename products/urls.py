from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # 1. Sửa lại tên thành 'product_list' để khớp chuẩn với file HTML
    path('', views.product_list, name='product_list'),
    
    # 2. Thêm đường dẫn cho chức năng TÌM KIẾM (Để ngay đây nhé)
    path('search/', views.search_products, name='search'), 
    
    # 3. Sửa lại tên thành 'product_detail' để khớp với thẻ <a> trong HTML
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    # Tìm kiếm sản phẩm:
    path('search/', views.search_products, name='search'),
]