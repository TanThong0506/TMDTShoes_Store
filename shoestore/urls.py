"""
URL configuration for shoestore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for shoestore project.
"""
"""
URL configuration for shoestore project.
"""
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
    
    path('cart/', include('cart.urls')), # <--- Thêm dòng này vào đây
    path('orders/', include('orders.urls', namespace='orders')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)