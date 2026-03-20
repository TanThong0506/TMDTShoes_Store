from django.shortcuts import render
<<<<<<< HEAD
from products.models import Product  # Đảm bảo đường dẫn import đúng app products

def home(request):
    # 1. Lấy 4 sản phẩm mới nhất dựa theo ID giảm dần
    latest_products = Product.objects.all().order_by('-id')[:4]
    
    # 2. Lấy 4 sản phẩm đang có giá khuyến mãi (discount_price không trống)
    # Chúng ta lọc những sản phẩm có discount_price lớn hơn 0
    sale_products = Product.objects.filter(discount_price__gt=0)[:4]
    
    context = {
        'latest_products': latest_products,
        'sale_products': sale_products,
    }
    
    return render(request, 'home.html', context)

def help_page(request):
    # Hàm xử lý cho trang trợ giúp mà bạn vừa làm layout
    return render(request, 'help.html')
=======

def home(request):
    return render(request, 'home.html')
>>>>>>> main
