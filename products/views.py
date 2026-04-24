from django.shortcuts import render, get_object_or_404, redirect # ĐÃ THÊM: redirect
from django.db.models import Q, F  # Dùng để so sánh 2 cột
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # BẮT BUỘC IMPORT ĐỂ PHÂN TRANG
from .models import Product, Category, Brand, StorePolicy, Size, Sale, Review # ĐÃ THÊM: Review
from .forms import ReviewForm # ĐÃ THÊM: ReviewForm
from django.utils import timezone
from django.contrib import messages # ĐÃ THÊM: messages

# --- PHẦN THÊM MỚI (CHỈ THÊM) ---
from django.contrib.auth.decorators import login_required
from orders.models import Order 
# ------------------------------

def home(request):
    # Lọc chuẩn giày Sale (Chỉ lấy những giày có giá gốc lớn hơn giá bán hiện tại)
    sale_products = Product.objects.filter(old_price__gt=F('price'), is_active=True).order_by('?')[:10]
    popular_categories = Category.objects.all()[:4] 
    latest_products = Product.objects.all().order_by('-id')[:8]
    
    # Lấy danh sách hãng để làm băng chuyền
    brands = Brand.objects.all() 
    
    context = {
        'sale_products': sale_products,
        'categories': popular_categories,
        'latest_products': latest_products,
        'brands': brands, # Truyền ra cho home.html
    }
    return render(request, 'home.html', context)

def product_list(request):
    # Lấy toàn bộ sản phẩm đang kinh doanh và SẮP XẾP THEO ID MỚI NHẤT
    # (Bắt buộc phải có order_by thì Paginator mới không bị lỗi mất sản phẩm)
    products = Product.objects.filter(is_active=True).order_by('-id')
    
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

    # === BẮT ĐẦU XỬ LÝ PHÂN TRANG (9 SẢN PHẨM / TRANG) ===
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # Nếu url không có số trang (ví dụ /products/), mặc định lấy trang 1
        page_obj = paginator.page(1)
    except EmptyPage:
        # Nếu người dùng nhập số trang quá lớn, tự động đưa về trang cuối cùng
        page_obj = paginator.page(paginator.num_pages)
    # === KẾT THÚC PHÂN TRANG ===

    brands = Brand.objects.all()
    categories = Category.objects.all()
    all_sizes = Size.objects.all()

    context = {
        # QUAN TRỌNG: Gán page_obj vào key 'products' để HTML cũ không bị lỗi trống trơn
        'products': page_obj, 
        # Vẫn giữ key 'page_obj' để HTML gọi ra các nút chuyển trang (1, 2, 3...)
        'page_obj': page_obj, 
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

    # === CHỈ THÊM: Logic xử lý Đánh giá sản phẩm ===
    reviews = product.reviews.all().order_by('-created_at')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần đăng nhập để đánh giá!")
            return redirect('login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Đánh giá của bạn đã được gửi!")
            return redirect('products:product_detail', pk=pk)
    else:
        form = ReviewForm()
    # =============================================

    context = {
        'product': product,
        'policy': policy,
        'recommended_products': recommended,
        'reviews': reviews, # THÊM VÀO CONTEXT
        'form': form,       # THÊM VÀO CONTEXT
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

# ==========================================
# HÀM LỊCH SỬ ĐƠN HÀNG (CHỈ THÊM MỚI)
# ==========================================
@login_required
def order_history(request):
    """
    Lấy danh sách đơn hàng của Nam để hiện vào menu dropdown Tài khoản
    """
    orders = Order.objects.filter(user=request.user).order_by('-id')
    return render(request, 'order_history.html', {'orders': orders})
@login_required
def order_detail(request, order_id):
    # Lấy đơn hàng đúng của người dùng đang đăng nhập, nếu không có trả về 404
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail_view.html', {'order': order})