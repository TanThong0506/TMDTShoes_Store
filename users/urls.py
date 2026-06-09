from django.urls import path
from . import views
from . import api

urlpatterns = [
    # Web views (keep for templates)
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # API endpoints
    path('api/register/', api.RegisterAPIView.as_view(), name='api_register'),
    path('api/logout/', api.LogoutAPIView.as_view(), name='api_logout'),
    path('api/token/', api.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', api.TokenRefreshView.as_view(), name='token_refresh'),
    # Thêm các đường dẫn cho tính năng Quên mật khẩu
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    
    # Tính năng cập nhật thông tin cá nhân
    path('profile/', views.profile_view, name='profile'),
    
    # Sổ địa chỉ
    path('address/add/', views.add_address, name='add_address'),
    path('address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('address/set-default/<int:address_id>/', views.set_default_address, name='set_default_address'),
]