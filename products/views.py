from django.shortcuts import render
from products.models import Product, Category, Brand

def home(request):
    # LỚP 1: Giới thiệu (Đã có trong Template, không cần xử lý data đặc biệt)
    
    # LỚP 2: Sản phẩm khuyến mãi (Lấy những món có discount_price)
    # Dùng order_by('?') để mỗi lần F5 khách lại thấy món mới ngẫu nhiên
    sale_products = Product.objects.filter(discount_price__gt=0).order_by('?')[:10]
    
    # LỚP 3: Danh mục phổ biến
    popular_categories = Category.objects.all()[:4] # Lấy 4 loại đầu tiên
    
    # LỚP 4: Sản phẩm mới nhất (Sản phẩm đã đăng)
    latest_products = Product.objects.all().order_by('-id')[:8]
    
    context = {
        'sale_products': sale_products,
        'categories': popular_categories,
        'latest_products': latest_products,
    }
    
    return render(request, 'home.html', context)

def product_list(request):
    # Giữ nguyên hàm này của bạn hoặc thêm bộ lọc checkbox như đã làm ở bước trước
    products = Product.objects.all()
    brands = Brand.objects.all()
    categories = Category.objects.all()
    
    # Lấy thêm all_sizes nếu bạn muốn hiện bộ lọc Size ở trang List
    from products.models import Size
    all_sizes = Size.objects.all()

    context = {
        'products': products,
        'brands': brands,
        'categories': categories,
        'all_sizes': all_sizes,
    }
    return render(request, 'products/list.html', context)