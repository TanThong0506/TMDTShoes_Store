"""
URL configuration for shoestore project.
"""
from django.contrib import admin
from django.urls import path, include
from . import views  # Giữ nguyên để dùng cho các trang như help_page
from products import views as product_views  # ĐÃ THÊM: Import views từ app products sang

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ĐÃ SỬA: Gọi hàm home từ product_views
    path('', product_views.home, name='home'),
    
    # Trang trợ giúp 
    path('help/', views.help_page, name='help'), 
    
    # ĐÃ SỬA: Gọi hàm sale_page từ product_views
    path('sale/', product_views.sale_page, name='sale'),
    
    # Kết nối tới App products
    path('products/', include('products.urls')), 
    # API xử lý Chatbot
    path('api/get_response/', views.get_response, name='get_response'),
    path('api/get_chat_history/', views.get_chat_history, name='get_chat_history'),
    
    # KẾT NỐI TỚI APP USERS 
    path('users/', include('users.urls')),
    
    path('cart/', include('cart.urls')), 
    # API endpoints for cart (REST-like)
    path('api/cart/', include('cart.api_urls')),
    # Central API router (DRF)
    path('api/', include('shoestore.api_urls')),
    path('orders/', include('orders.urls', namespace='orders')),

    # ========================================================
    # CHỈ THÊM: ĐƯỜNG DẪN HỖ TRỢ QUÊN MẬT KHẨU (KHÔNG SỬA CŨ)
    # ========================================================
    path('forgot-password/', include('users.urls')), 
    path('verify-otp/', include('users.urls')),
    path('reset-password/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)