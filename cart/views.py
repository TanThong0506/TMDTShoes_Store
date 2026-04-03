from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Cart, CartItem
from products.models import Product


def _get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key or request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


def _item_data(item):
    return {
        'id': item.id,
        'product_id': item.product.id,
        'name': item.product.name,
        'size': item.size,
        'quantity': item.quantity,
        'price': item.product.price,
        'subtotal': item.subtotal,
    }


def cart_page(request):
    cart = _get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    context = {
        'cart': cart,
        'items': items,
        'total_amount': cart.total_amount,
    }
    return render(request, 'cart/cart.html', context)


@require_http_methods(['GET'])
def cart_items(request):
    cart = _get_or_create_cart(request)
    items = [ _item_data(item) for item in cart.items.select_related('product').all() ]
    return JsonResponse({'items': items, 'total_amount': cart.total_amount})


@require_http_methods(['POST'])
@csrf_exempt
def add_to_cart(request):
    if request.content_type == 'application/json':
        import json
        data = json.loads(request.body.decode('utf-8') or '{}')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        size = data.get('size')
    else:
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity', 1)
        size = request.POST.get('size')

    if not product_id or not str(product_id).isdigit():
        return HttpResponseBadRequest('product_id không hợp lệ')

    product = get_object_or_404(Product, id=product_id, is_active=True)

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return HttpResponseBadRequest('quantity phải là số nguyên dương')

    if quantity < 1:
        return HttpResponseBadRequest('quantity phải lớn hơn 0')

    if product.sizes.exists() and not size:
        return HttpResponseBadRequest('Phải chọn size')

    cart = _get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, size=size or '', defaults={'quantity': quantity})
    if not created:
        item.quantity += quantity
        item.save()

    if request.META.get('HTTP_ACCEPT') == 'application/json' or request.content_type == 'application/json':
        return JsonResponse({'item': _item_data(item), 'total_amount': cart.total_amount, 'created': created})

    messages.success(request, f"Đã thêm {product.name} (x{quantity}) vào giỏ hàng")
    return redirect('cart:cart_page')


@require_http_methods(['PATCH', 'PUT', 'POST'])
@csrf_exempt
def update_cart_item(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if request.content_type == 'application/json':
        import json
        data = json.loads(request.body.decode('utf-8') or '{}')
        quantity = data.get('quantity')
    else:
        quantity = request.POST.get('quantity')

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        return HttpResponseBadRequest('quantity phải là số nguyên dương')

    if quantity < 1:
        return HttpResponseBadRequest('quantity phải lớn hơn 0')

    item.quantity = quantity
    item.save()

    return JsonResponse({'item': _item_data(item), 'total_amount': cart.total_amount})


@require_http_methods(['DELETE', 'POST'])
@csrf_exempt
def delete_cart_item(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return JsonResponse({'deleted': True, 'total_amount': cart.total_amount})


@require_http_methods(['POST'])
@csrf_exempt
def clear_cart(request):
    cart = _get_or_create_cart(request)
    cart.items.all().delete()
    return JsonResponse({'cleared': True, 'total_amount': 0})
