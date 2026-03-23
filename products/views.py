from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F  # ĐÃ THÊM F: Dùng để so sánh 2 cột
from .models import Product, Category, Brand, StorePolicy, Size

def home(request):
    # Lọc chuẩn giày Sale (Chỉ lấy những giày có giá gốc lớn hơn giá bán hiện tại)
    sale_products = Product.objects.filter(old_price__gt=F('price'), is_active=True).order_by('?')[:10]
    popular_categories = Category.objects.all()[:4] 
    latest_products = Product.objects.all().order_by('-id')[:8]
    
    context = {
        'sale_products': sale_products,
        'categories': popular_categories,
        'latest_products': latest_products,
    }
    return render(request, 'home.html', context)

def product_list(request):
    # Lấy toàn bộ sản phẩm đang kinh doanh làm nền tảng ban đầu
    products = Product.objects.filter(is_active=True)
    
    # === BẮT ĐẦU XỬ LÝ BỘ LỌC TỪ URL ===
    brand_ids = request.GET.getlist('brand')
    if brand_ids:
        products = products.filter(brand__id__in=brand_ids)
        
    category_ids = request.GET.getlist('category')
    if category_ids:
        products = products.filter(category__id__in=category_ids)
        
    size_ids = request.GET.getlist('size')
    if size_ids:
        products = products.filter(sizes__id__in=size_ids)
        
    # Loại bỏ các kết quả trùng lặp
    products = products.distinct()
    # === KẾT THÚC XỬ LÝ BỘ LỌC ===

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
# HÀM TÌM KIẾM SẢN PHẨM (ĐÃ NÂNG CẤP)
# ==========================================
def search_products(request):
    query = request.GET.get('q', '') 
    results = [] 

    if query:
        # TÌM KIẾM ĐA NĂNG: Tên, Hãng, Loại, và cả Size
        results = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(sizes__value__icontains=query)  # ĐÃ FIX: Dùng sizes__value và thêm dấu |
        ).distinct()

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'products/search.html', context)

# ==========================================
# HÀM TRANG KHUYẾN MÃI (ĐÃ THÊM TÍNH NĂNG SẮP XẾP)
# ==========================================
def sale_page(request):
    # 1. Lọc ra các sản phẩm ĐANG GIẢM GIÁ (có giá cũ lớn hơn giá hiện tại)
    sale_items = Product.objects.filter(is_active=True, old_price__gt=F('price'))
    
    # 2. BẮT ĐẦU XỬ LÝ SẮP XẾP TỪ URL
    sort_by = request.GET.get('sort', 'hot') # Mặc định là 'hot' nếu không bấm gì
    
    if sort_by == 'asc':
        # Giá từ thấp đến cao
        sale_items = sale_items.order_by('price')
    elif sort_by == 'desc':
        # Giá từ cao đến thấp
        sale_items = sale_items.order_by('-price')
    else:
        # Khuyến mãi hot nhất (Sắp xếp theo số tiền được giảm nhiều nhất)
        sale_items = sale_items.annotate(discount_amount=F('old_price') - F('price')).order_by('-discount_amount')

    # 3. Trả về giao diện (ĐÃ SỬA: Thêm 'current_sort' vào context)
    context = {
        'sale_items': sale_items,
        'current_sort': sort_by, 
    }
    return render(request, 'sale.html', context)