from django.shortcuts import render
from products.models import Product, Category  # Đừng quên import Category nhé!

def home(request):
    # 1. Sản phẩm khuyến mãi (Lấy ngẫu nhiên 10 món để cuộn ngang)
    sale_products = Product.objects.filter(old_price__gt=0).order_by('?')[:10]
    
    # 2. Danh mục phổ biến (Lấy 4 loại hiển thị ra trang chủ)
    categories = Category.objects.all()[:4]
    
    # 3. Sản phẩm mới nhất (Lấy 8 món mới nhất)
    latest_products = Product.objects.all().order_by('-id')[:8]
    
    context = {
        'sale_products': sale_products,
        'categories': categories,
        'latest_products': latest_products,
    }
    
    return render(request, 'home.html', context)

def help_page(request):
    # Hàm xử lý cho trang trợ giúp
    return render(request, 'help.html')

# THÊM HÀM NÀY ĐỂ XỬ LÝ TRANG KHUYẾN MÃI (SALE)
# SỬA LẠI HÀM NÀY
def sale_page(request):
    sale_items = Product.objects.filter(old_price__gt=0).order_by('-id')
    return render(request, 'sale.html', {'sale_items': sale_items})