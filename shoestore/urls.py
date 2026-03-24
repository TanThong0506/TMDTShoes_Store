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
    
    # KẾT NỐI TỚI APP USERS 
    path('users/', include('users.urls')),
    
    # 👇 DÒNG QUAN TRỌNG
    path('cart/', product_views.cart_view, name='cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)