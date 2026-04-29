from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category, Brand, StorePolicy, Size, Sale, Review
from .forms import ReviewForm
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def home(request):
    # Lọc giày Sale và sản phẩm mới nhất
    sale_products = Product.objects.filter(old_price__gt=F('price'), is_active=True).order_by('?')[:10]
    popular_categories = Category.objects.all()[:4] 
    latest_products = Product.objects.filter(is_active=True).order_by('-id')[:8]
    brands = Brand.objects.all() 
    
    context = {
        'sale_products': sale_products,
        'categories': popular_categories,
        'latest_products': latest_products,
        'brands': brands,
    }
    return render(request, 'home.html', context)

def product_list(request):
    products = Product.objects.filter(is_active=True).order_by('-id')
    
    # --- Xử lý bộ lọc ---
    raw_brands = request.GET.getlist('brand')
    if raw_brands:
        products = products.filter(brand__id__in=[b for b in raw_brands if b.isdigit()])
        
    raw_categories = request.GET.getlist('category')
    if raw_categories:
        products = products.filter(category__id__in=[c for c in raw_categories if c.isdigit()])
        
    raw_sizes = request.GET.getlist('size')
    if raw_sizes:
        products = products.filter(sizes__id__in=[s for s in raw_sizes if s.isdigit()])
        
    products = products.distinct()

    # --- Phân trang ---
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    context = {
        'products': page_obj, 
        'page_obj': page_obj, 
        'brands': Brand.objects.all(),
        'categories': Category.objects.all(),
        'all_sizes': Size.objects.all(),
    }
    return render(request, 'products/list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    policy = StorePolicy.objects.first() 
    
    # Dùng hàm từ Model để lấy sản phẩm gợi ý (Đã tối ưu ở bước trước)
    recommended = product.get_recommended()
    
    # Xử lý đánh giá
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
            messages.success(request, "Cảm ơn Nam, đánh giá đã được gửi!")
            return redirect('products:product_detail', pk=pk)
    else:
        form = ReviewForm()

    context = {
        'product': product,
        'policy': policy,
        'recommended_products': recommended,
        'reviews': reviews,
        'form': form,
        'average_rating': product.get_average_rating(), # Lấy từ model
    }
    return render(request, 'products/product_detail.html', context)

def search_products(request):
    query = request.GET.get('q', '').strip() 
    results = [] 
    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(sizes__value__icontains=query)  
        ).distinct()
    return render(request, 'products/search.html', {'query': query, 'results': results})

def sale_page(request):
    now = timezone.now()
    active_sale = Sale.objects.filter(active=True, start_date__lte=now, end_date__gte=now).order_by('-start_date').first()
    
    if active_sale:
        sale_items = active_sale.products.filter(is_active=True).distinct()
    else:
        sale_items = Product.objects.filter(is_active=True, old_price__gt=F('price'))
    
    sort_by = request.GET.get('sort', 'hot')
    if sort_by == 'asc':
        sale_items = sale_items.order_by('price')
    elif sort_by == 'desc':
        sale_items = sale_items.order_by('-price')
    else:
        sale_items = sale_items.annotate(discount_amount=F('old_price') - F('price')).order_by('-discount_amount')

    return render(request, 'sale.html', {
        'sale_items': sale_items,
        'current_sort': sort_by, 
        'active_sale': active_sale,
    })

# --- SỬA VÀ XÓA ĐÁNH GIÁ (GIỮ NGUYÊN LOGIC CỦA NAM) ---
@login_required
def edit_review(request):
    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        review = get_object_or_404(Review, id=review_id, user=request.user)
        review.rating = request.POST.get('rating')
        review.comment = request.POST.get('comment')
        review.save()
        messages.success(request, "Đã cập nhật đánh giá!")
        return redirect('products:product_detail', pk=review.product.pk)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_pk = review.product.pk
    review.delete()
    messages.success(request, "Đã xóa đánh giá!")
    return redirect('products:product_detail', pk=product_pk)