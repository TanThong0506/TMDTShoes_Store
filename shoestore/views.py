from django.shortcuts import render
# 1. ĐÃ SỬA: Import thêm Brand từ products.models
from products.models import Product, Brand 

def home(request):
    # Sản phẩm khuyến mãi (Lấy ngẫu nhiên 10 món để cuộn ngang)
    sale_products = Product.objects.filter(old_price__gt=0).order_by('?')[:10]
    
    # 2. ĐÃ SỬA: Lấy TẤT CẢ Thương hiệu (Brand) để làm dải băng chuyền
    all_brands = Brand.objects.all()
    
    # Sản phẩm mới nhất (Lấy 8 món mới nhất)
    latest_products = Product.objects.all().order_by('-id')[:8]
    
    context = {
        'sale_products': sale_products,
        'brands': all_brands, # 3. ĐÃ SỬA: Truyền brands ra ngoài template
        'latest_products': latest_products,
    }
    
    return render(request, 'home.html', context)

def help_page(request):
    # Hàm xử lý cho trang trợ giúp
    return render(request, 'help.html')

def sale_page(request):
    # Hàm xử lý trang khuyến mãi
    sale_items = Product.objects.filter(old_price__gt=0).order_by('-id')
    return render(request, 'sale.html', {'sale_items': sale_items})