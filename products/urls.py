from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('search/', views.search_products, name='search'), 
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # URL cho tính năng Sửa và Xóa đánh giá
    path('review/edit/', views.edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
]