from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # 1. Trang danh sách sản phẩm
    path('', views.product_list, name='product_list'),
    
    # 2. Chức năng tìm kiếm (Chỉ giữ lại 1 dòng này thôi)
    path('search/', views.search_products, name='search'), 
    
    # 3. Trang chi tiết sản phẩm
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
]