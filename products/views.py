from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product, Category, Brand, Cart, CartItem, Size
import random
from .models import Order, OrderItem
# ================= HOME =================

def home(request):
    sale_products = Product.objects.filter(discount_price__gt=0).order_by('?')[:10]
    popular_categories = Category.objects.all()[:4]
    latest_products = Product.objects.all().order_by('-id')[:8]

    return render(request, 'home.html', {
        'sale_products': sale_products,
        'categories': popular_categories,
        'latest_products': latest_products,
    })


# ================= PRODUCT =================

def product_list(request):
    products = Product.objects.all()
    brands = Brand.objects.all()
    categories = Category.objects.all()
    sizes = Size.objects.all()

    return render(request, 'products/list.html', {
        'products': products,
        'brands': brands,
        'categories': categories,
        'all_sizes': sizes,
    })


def product_detail(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'products/product_detail.html', {
        'product': product
    })


# ================= GIỎ HÀNG =================

def get_cart(request):
    cart_id = request.session.get('cart_id')

    if cart_id:
        return Cart.objects.get(id=cart_id)

    cart = Cart.objects.create()
    request.session['cart_id'] = cart.id
    return cart


def cart_view(request):
    cart = get_cart(request)
    items = CartItem.objects.filter(cart=cart)

    total = 0
    for item in items:
        total += item.total_price()

    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    size_id = request.POST.get('size')
    size = get_object_or_404(Size, id=size_id)

    cart = get_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size
    )

    if not created:
        item.quantity += 1

    item.save()
    return redirect('products:cart')


def increase(request, item_id):
    item = CartItem.objects.get(id=item_id)
    item.quantity += 1
    item.save()
    return redirect('products:cart')


def decrease(request, item_id):
    item = CartItem.objects.get(id=item_id)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('products:cart')


def remove_item(request, item_id):
    item = CartItem.objects.get(id=item_id)
    item.delete()
    return redirect('products:cart')


def checkout(request):
    cart = get_cart(request)
    items = CartItem.objects.filter(cart=cart)

    if not items:
        return redirect('products:cart')

    total = sum(item.total_price() for item in items)

    # 🔥 tạo đơn hàng
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total=total
    )

    # 🔥 lưu sản phẩm vào OrderItem
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            size=item.size,
            quantity=item.quantity,
            price=item.get_price()
        )

    # ❌ xóa giỏ hàng
    items.delete()

    return render(request, 'success.html', {
        'total': total,
        'order_code': order.id
    })