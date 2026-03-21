from django.shortcuts import render, get_object_or_404
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