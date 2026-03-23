from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn này kết hợp với 'users/' ở trên sẽ tạo thành 'users/login/'
    path('login/', views.login_view, name='login'),
    
    # THÊM DÒNG NÀY VÀO
    path('register/', views.register_view, name='register'),
    
    # THÊM TIẾP DÒNG NÀY VÀO ĐỂ SỬA LỖI ĐĂNG XUẤT NHÉ
    path('logout/', views.logout_view, name='logout'),
]