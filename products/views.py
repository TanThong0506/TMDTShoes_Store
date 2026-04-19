from django.shortcuts import render, get_object_or_404
from django.db.models import Q, F  # ĐÃ THÊM F: Dùng để so sánh 2 cột
from .models import Product, Category, Brand, StorePolicy, Size, Sale
from django.utils import timezone

def home(request):
    # Lọc chuẩn giày Sale (Chỉ lấy những giày có giá gốc lớn hơn giá bán hiện tại)
    sale_products = Product.objects.filter(old_price__gt=F('price'), is_active=True).order_by('?')[:10]
    popular_categories = Category.objects.all()[:4] 
    latest_products = Product.objects.all().order_by('-id')[:8]
    
    # ĐÃ THÊM LẠI: Lấy danh sách hãng để làm băng chuyền
    brands = Brand.objects.all() 
    
    context = {
        'sale_products': sale_products,
        'categories': popular_categories,
        'latest_products': latest_products,
        'brands': brands, # Truyền ra cho home.html
    }
    return render(request, 'home.html', context)

def product_list(request):
    # Lấy toàn bộ sản phẩm đang kinh doanh làm nền tảng ban đầu
    products = Product.objects.filter(is_active=True)
    
    # === VALIDATION: BẮT ĐẦU XỬ LÝ BỘ LỌC TỪ URL ===
    # Chỉ giữ lại các ID là chữ số (chống hacker hoặc lỗi gõ nhầm chữ)
    raw_brands = request.GET.getlist('brand')
    brand_ids = [bid for bid in raw_brands if bid.isdigit()]
    if brand_ids:
        products = products.filter(brand__id__in=brand_ids)
        
    raw_categories = request.GET.getlist('category')
    category_ids = [cid for cid in raw_categories if cid.isdigit()]
    if category_ids:
        products = products.filter(category__id__in=category_ids)
        
    raw_sizes = request.GET.getlist('size')
    size_ids = [sid for sid in raw_sizes if sid.isdigit()]
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
    # Sản phẩm đề cử: ưu tiên cùng category, loại trừ product hiện tại
    recommended = Product.objects.filter(category__in=product.category.all(), is_active=True).exclude(pk=product.pk).distinct()
    # Nếu không đủ, thêm theo brand
    if recommended.count() < 6:
        more = Product.objects.filter(brand=product.brand, is_active=True).exclude(pk=product.pk).distinct()
        # Kết hợp và loại trùng
        recommended = (recommended | more).distinct()

    # Fallback: nếu vẫn ít, lấy sản phẩm mới nhất
    if recommended.count() < 6:
        fallback = Product.objects.filter(is_active=True).exclude(pk=product.pk).order_by('-id')
        # Tìm dòng 75 và sửa thành như sau:
        recommended_ids = list(recommended.values_list('id', flat=True)) + \
                        list(fallback.values_list('id', flat=True))

        recommended = Product.objects.filter(id__in=recommended_ids).distinct()

        recommended = recommended.order_by('?')[:8]

    context = {
        'product': product,
        'policy': policy,
        'recommended_products': recommended,
    }
    return render(request, 'products/product_detail.html', context)

# ==========================================
# HÀM TÌM KIẾM SẢN PHẨM (ĐÃ THÊM VALIDATION)
# ==========================================
def search_products(request):
    # VALIDATION 1: Loại bỏ khoảng trắng thừa ở 2 đầu (VD: "  nike " -> "nike")
    query = request.GET.get('q', '').strip() 
    
    # VALIDATION 2: Giới hạn độ dài từ khóa (Tránh việc cố tình nhập quá dài làm sập DB)
    if len(query) > 100:
        query = query[:100]

    results = [] 

    if query:
        # TÌM KIẾM ĐA NĂNG: Tên, Hãng, Loại, và cả Size
        results = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(sizes__value__icontains=query)  
        ).distinct()

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'products/search.html', context)

# ==========================================
# HÀM TRANG KHUYẾN MÃI (ĐÃ THÊM VALIDATION)
# ==========================================
def sale_page(request):
    now = timezone.now()
    # 1. Nếu có chương trình Sale đang active (theo ngày) thì lấy các sản phẩm đó
    active_sale = Sale.objects.filter(active=True, start_date__lte=now, end_date__gte=now).order_by('-start_date').first()
    if active_sale:
        sale_items = active_sale.products.filter(is_active=True).distinct()
    else:
        # Fallback: Lọc ra các sản phẩm ĐANG GIẢM GIÁ (có giá cũ lớn hơn giá hiện tại)
        sale_items = Product.objects.filter(is_active=True, old_price__gt=F('price'))
    
    # 2. BẮT ĐẦU XỬ LÝ SẮP XẾP TỪ URL
    # VALIDATION: Loại bỏ khoảng trắng thừa (nếu có)
    sort_by = request.GET.get('sort', 'hot').strip() 
    
    if sort_by == 'asc':
        # Giá từ thấp đến cao
        sale_items = sale_items.order_by('price')
    elif sort_by == 'desc':
        # Giá từ cao đến thấp
        sale_items = sale_items.order_by('-price')
    else:
        # VALIDATION: Nếu người dùng nhập linh tinh (không phải asc hay desc),
        # tự động gán lại thành 'hot' và xếp theo khuyến mãi tốt nhất.
        sort_by = 'hot'
        sale_items = sale_items.annotate(discount_amount=F('old_price') - F('price')).order_by('-discount_amount')

    # 3. Trả về giao diện 
    context = {
        'sale_items': sale_items,
        'current_sort': sort_by, 
        'active_sale': active_sale,
    }
    return render(request, 'sale.html', context)