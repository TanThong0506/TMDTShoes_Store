from django.shortcuts import render, get_object_or_404
from django.db.models import Q  # BẮT BUỘC PHẢI THÊM DÒNG NÀY ĐỂ TÌM KIẾM
from .models import Product, Category, Brand, StorePolicy, Size

def home(request):
    sale_products = Product.objects.filter(old_price__gt=0).order_by('?')[:10]
    popular_categories = Category.objects.all()[:4] 
    latest_products = Product.objects.all().order_by('-id')[:8]
    
    context = {
        'sale_products': sale_products,
        'categories': popular_categories,
        'latest_products': latest_products,
    }
    return render(request, 'home.html', context)

def product_list(request):
    products = Product.objects.all()
    brands = Brand.objects.all()
    categories = Category.objects.all()
    all_sizes = Size.objects.all()

    context = {
        'products': products,
        'brands': brands,
        'categories': categories,
        'all_sizes': all_sizes,
    }
    return render(request, 'products/list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Lấy chính sách chung
    policy = StorePolicy.objects.first() 
    
    context = {
        'product': product,
        'policy': policy,
    }
    return render(request, 'products/product_detail.html', context)

# ==========================================
# HÀM TÌM KIẾM SẢN PHẨM (MỚI THÊM)
# ==========================================
def search_products(request):
    # Lấy từ khóa khách hàng gõ từ thanh tìm kiếm (biến 'q')
    query = request.GET.get('q', '') 
    results = [] 

    if query:
        # Tìm kiếm theo tên sản phẩm HOẶC tên thương hiệu
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(brand__name__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'products/search.html', context)