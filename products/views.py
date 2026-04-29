from django.shortcuts import render, get_object_or_404, redirect # ĐÃ THÊM: redirect
from django.db.models import Q, F  # Dùng để so sánh 2 cột
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # BẮT BUỘC IMPORT ĐỂ PHÂN TRANG
from .models import Product, Category, Brand, StorePolicy, Size, Sale, Review # ĐÃ THÊM: Review
from .forms import ReviewForm # ĐÃ THÊM: ReviewForm
from django.utils import timezone
from django.contrib import messages # ĐÃ THÊM: messages
from django.contrib.auth.decorators import login_required # CHỈ THÊM ĐỂ BẢO MẬT HÀM XÓA/SỬA

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
    products = Product.objects.filter(is_active=True).order_by('-id')
    
    # === VALIDATION: BẮT ĐẦU XỬ LÝ BỘ LỌC TỪ URL ===
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
        
    products = products.distinct()
    # === KẾT THÚC XỬ LÝ BỘ LỌC ===

    # === BẮT ĐẦU XỬ LÝ PHÂN TRANG (9 SẢN PHẨM / TRANG) ===
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    brands = Brand.objects.all()
    categories = Category.objects.all()
    all_sizes = Size.objects.all()

    context = {
        'products': page_obj, 
        'page_obj': page_obj, 
        'brands': brands,
        'categories': categories,
        'all_sizes': all_sizes,
    }
    return render(request, 'products/list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    policy = StorePolicy.objects.first() 
    recommended = Product.objects.filter(category__in=product.category.all(), is_active=True).exclude(pk=product.pk).distinct()
    
    if recommended.count() < 6:
        more = Product.objects.filter(brand=product.brand, is_active=True).exclude(pk=product.pk).distinct()
        recommended = (recommended | more).distinct()

    if recommended.count() < 6:
        fallback = Product.objects.filter(is_active=True).exclude(pk=product.pk).order_by('-id')
        recommended_ids = list(recommended.values_list('id', flat=True)) + \
                        list(fallback.values_list('id', flat=True))
        recommended = Product.objects.filter(id__in=recommended_ids).distinct()
        recommended = recommended.order_by('?')[:8]

    # === Logic xử lý Đánh giá sản phẩm ===
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

    context = {
        'product': product,
        'policy': policy,
        'recommended_products': recommended,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'products/product_detail.html', context)

def search_products(request):
    query = request.GET.get('q', '').strip() 
    if len(query) > 100:
        query = query[:100]

    results = [] 
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(sizes__value__icontains=query)  
        ).distinct()

    context = { 'query': query, 'results': results }
    return render(request, 'products/search.html', context)

def sale_page(request):
    now = timezone.now()
    active_sale = Sale.objects.filter(active=True, start_date__lte=now, end_date__gte=now).order_by('-start_date').first()
    if active_sale:
        sale_items = active_sale.products.filter(is_active=True).distinct()
    else:
        sale_items = Product.objects.filter(is_active=True, old_price__gt=F('price'))
    
    sort_by = request.GET.get('sort', 'hot').strip() 
    if sort_by == 'asc':
        sale_items = sale_items.order_by('price')
    elif sort_by == 'desc':
        sale_items = sale_items.order_by('-price')
    else:
        sort_by = 'hot'
        sale_items = sale_items.annotate(discount_amount=F('old_price') - F('price')).order_by('-discount_amount')

    context = {
        'sale_items': sale_items,
        'current_sort': sort_by, 
        'active_sale': active_sale,
    }
    return render(request, 'sale.html', context)

# ==========================================
# CHỈ THÊM: HÀM SỬA VÀ XÓA ĐÁNH GIÁ
# ==========================================

@login_required
def edit_review(request):
    """Xử lý cập nhật nội dung và số sao của đánh giá"""
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        # Đảm bảo chỉ người tạo ra review mới được sửa
        review = get_object_or_404(Review, id=review_id, user=request.user)
        
        review.rating = request.POST.get('rating')
        review.comment = request.POST.get('comment')
        review.save()
        
        messages.success(request, "Cập nhật đánh giá thành công!")
        return redirect('products:product_detail', pk=review.product.pk)

@login_required
def delete_review(request, review_id):
    """Xử lý xóa vĩnh viễn đánh giá"""
    # Đảm bảo chỉ người tạo hoặc admin mới được xóa
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_pk = review.product.pk
    review.delete()
    
    messages.success(request, "Đã xóa đánh giá!")
    return redirect('products:product_detail', pk=product_pk)