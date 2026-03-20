from django.shortcuts import render  
from .models import Product, Brand, Category # Đảm bảo đã import các model này nếu bạn dùng chúng

def product_list(request):
    # Giả sử bạn đang lấy dữ liệu như thế này:
    products = Product.objects.all()
    brands = Brand.objects.all()
    categories = Category.objects.all()

    context = {
        'products': products,
        'brands': brands,
        'categories': categories,
    }
    # Lỗi xảy ra ở dòng dưới đây vì chưa có 'render' ở trên
    return render(request, 'products/list.html', context)