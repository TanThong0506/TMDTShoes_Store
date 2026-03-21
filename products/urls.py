from django.urls import path
from . import views
app_name = 'products'
urlpatterns = [
    # Trang danh sách sản phẩm (http://127.0.0.1:8000/products/)
    path('', views.product_list, name='product_list'),
    
    # Trang chi tiết sản phẩm (Ví dụ: http://127.0.0.1:8000/products/product/1/)
    # <int:pk> là ID của đôi giày Nam bấm vào
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
]