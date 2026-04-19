from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from products.models import Product
from django.contrib.humanize.templatetags.humanize import intcomma
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import random # Thêm cái này ở đầu file để tạo mã đơn hàng ngẫu nhiên

# Hàm phụ trợ xử lý cả 2 loại dữ liệu (int của web và dict của chatbot)
def _get_cart_data(cart):
    total = 0
    for item_key, item_val in cart.items():
        # Trích xuất đúng số lượng bất kể là int hay dict
        quantity = item_val['quantity'] if isinstance(item_val, dict) else item_val
        try:
            p_id = item_key.split('_')[0]
            product = Product.objects.get(id=int(p_id))
            total += product.price * quantity
        except:
            continue
    return total

def cart_detail(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    product_ids_in_cart = [] # Danh sách ID để loại trừ sản phẩm đã có trong giỏ

    for item_key, item_val in cart.items():
        quantity = item_val['quantity'] if isinstance(item_val, dict) else item_val
        try:
            parts = item_key.split('_')
            p_id = parts[0]
            product_ids_in_cart.append(int(p_id)) # Thêm ID vào danh sách loại trừ
            
            size = parts[1] if len(parts) > 1 else "N/A"
            product = Product.objects.get(id=int(p_id))
            item_total = product.price * quantity
            total += item_total
            items.append({
                'product': product,
                'quantity': quantity,
                'size': size,
                'item_key': item_key,
                'total_price': item_total,
            })
        except (Product.DoesNotExist, ValueError, IndexError):
            continue 

    # --- PHẦN GỢI Ý SẢN PHẨM (SỬA Ở ĐÂY) ---
    # Lấy 4 sản phẩm ngẫu nhiên không có trong giỏ hàng
    recommended_products = Product.objects.exclude(id__in=product_ids_in_cart).order_by('?')[:4]
    
    # Nếu không còn sản phẩm nào để loại trừ, lấy 4 sản phẩm bất kỳ
    if not recommended_products.exists():
        recommended_products = Product.objects.all()[:4]
    # ---------------------------------------

    return render(request, 'cart.html', {
        'items': items, 
        'total': total,
        'recommended_products': recommended_products # Truyền biến này ra template
    })

def add_to_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1
        size = request.POST.get('size', 'N/A')
        item_key = f"{product_id}_{size}"
        
        # Tương thích cộng dồn cho cả 2 kiểu dữ liệu
        if item_key in cart:
            if isinstance(cart[item_key], dict):
                cart[item_key]['quantity'] += quantity
            else:
                cart[item_key] += quantity
        else:
            cart[item_key] = quantity
        
        request.session['cart'] = cart
        # Tính tổng số lượng hiển thị trên icon
        new_count = sum(v['quantity'] if isinstance(v, dict) else v for v in cart.values())
        request.session['cart_count'] = new_count
        request.session.modified = True
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'cart_count': new_count})
        return redirect('cart:cart_detail')
    return redirect('home')

def update_cart(request, item_key, action):
    cart = request.session.get('cart', {})
    item_total_html = "0"
    current_qty = 0
    
    if item_key in cart:
        is_dict = isinstance(cart[item_key], dict)
        current_qty = cart[item_key]['quantity'] if is_dict else cart[item_key]
        
        if action == 'increase':
            current_qty += 1
        elif action == 'decrease':
            current_qty -= 1
            
        if current_qty <= 0:
            del cart[item_key]
        else:
            if is_dict:
                cart[item_key]['quantity'] = current_qty
            else:
                cart[item_key] = current_qty
        
        if item_key in cart:
            p_id = item_key.split('_')[0]
            product = Product.objects.get(id=int(p_id))
            item_total_html = intcomma(product.price * current_qty)

    request.session['cart'] = cart
    new_count = sum(v['quantity'] if isinstance(v, dict) else v for v in cart.values())
    request.session['cart_count'] = new_count
    request.session.modified = True
    
    new_total_cart = _get_cart_data(cart)
    
    return JsonResponse({
        'success': True, 
        'cart_count': new_count,
        'item_count': current_qty if item_key in cart else 0,
        'item_total': item_total_html,
        'total_cart': intcomma(new_total_cart)
    })

def remove_from_cart(request, item_key):
    cart = request.session.get('cart', {})
    if item_key in cart:
        del cart[item_key]
        
    request.session['cart'] = cart
    new_count = sum(v['quantity'] if isinstance(v, dict) else v for v in cart.values())
    request.session['cart_count'] = new_count
    request.session.modified = True
    
    new_total_cart = _get_cart_data(cart)
    
    return JsonResponse({
        'success': True,
        'cart_count': new_count,
        'total_cart': intcomma(new_total_cart)
    })

def checkout(request):
    cart = request.session.get('cart', {})
    item_keys_str = request.GET.get('items', '')
    
    if not item_keys_str:
        return redirect('cart:cart_detail')
    
    selected_keys = item_keys_str.split(',')
    checkout_items = []
    total_price = 0
    
    for key in selected_keys:
        if key in cart:
            try:
                parts = key.split('_')
                product_id = parts[0]
                size = parts[1] if len(parts) > 1 else "N/A"
                
                quantity = cart[key]['quantity'] if isinstance(cart[key], dict) else cart[key]
                
                product = Product.objects.get(id=int(product_id))
                item_total = product.price * quantity
                total_price += item_total
                
                checkout_items.append({
                    'item_key': key,
                    'product': product,
                    'quantity': quantity,
                    'size': size,
                    'total_price': item_total,
                })
            except (Product.DoesNotExist, ValueError, IndexError):
                continue

    # --- PHẦN THÊM MỚI ĐỂ QUÉT MÃ QR ---
    # Tạo một mã đơn hàng ngẫu nhiên để làm nội dung chuyển khoản cho chuyên nghiệp
    order_id = random.randint(100000, 999999) 
    
    context = {
        'items': checkout_items,
        'total_price': total_price,
        'order_id': order_id, # Truyền cái này sang để hiện "Nội dung: DH123456"
    }
    return render(request, 'checkout.html', context)


# -------------------- API wrapper views --------------------
@csrf_exempt
@require_http_methods(["GET"])
def api_get_cart(request):
    cart = request.session.get('cart', {})
    items = []
    for item_key, item_val in cart.items():
        quantity = item_val['quantity'] if isinstance(item_val, dict) else item_val
        try:
            parts = item_key.split('_')
            p_id = parts[0]
            size = parts[1] if len(parts) > 1 else "N/A"
            product = Product.objects.get(id=int(p_id))
            items.append({
                'item_key': item_key,
                'product_id': product.id,
                'name': getattr(product, 'name', str(product)),
                'price': float(product.price),
                'quantity': quantity,
                'size': size,
            })
        except Exception:
            continue

    total = _get_cart_data(cart)
    cart_count = sum(v['quantity'] if isinstance(v, dict) else v for v in cart.values())
    return JsonResponse({'items': items, 'total': float(total), 'cart_count': cart_count})


@csrf_exempt
@require_http_methods(["POST"])
def api_add_to_cart(request):
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
    except Exception:
        data = {}

    product_id = data.get('product_id') or request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'success': False, 'error': 'product_id required'}, status=400)

    try:
        quantity = int(data.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    size = data.get('size', 'N/A')

    cart = request.session.get('cart', {})
    item_key = f"{product_id}_{size}"

    if item_key in cart:
        if isinstance(cart[item_key], dict):
            cart[item_key]['quantity'] += quantity
        else:
            cart[item_key] += quantity
    else:
        cart[item_key] = quantity

    request.session['cart'] = cart
    new_count = sum(v['quantity'] if isinstance(v, dict) else v for v in cart.values())
    request.session['cart_count'] = new_count
    request.session.modified = True

    return JsonResponse({'success': True, 'cart_count': new_count})


@csrf_exempt
@require_http_methods(["POST"])
def api_update_cart(request):
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
    except Exception:
        data = {}

    item_key = data.get('item_key') or request.POST.get('item_key')
    action = data.get('action') or request.POST.get('action')
    quantity = data.get('quantity')

    if not item_key:
        return JsonResponse({'success': False, 'error': 'item_key required'}, status=400)

    cart = request.session.get('cart', {})
    if item_key not in cart:
        return JsonResponse({'success': False, 'error': 'item not found'}, status=404)

    is_dict = isinstance(cart[item_key], dict)
    current_qty = cart[item_key]['quantity'] if is_dict else cart[item_key]

    if quantity is not None:
        try:
            current_qty = int(quantity)
        except (ValueError, TypeError):
            pass
    elif action == 'increase':
        current_qty += 1
    elif action == 'decrease':
        current_qty -= 1

    if current_qty <= 0:
        del cart[item_key]
        current_qty = 0
    else:
        if is_dict:
            cart[item_key]['quantity'] = current_qty
        else:
            cart[item_key] = current_qty

    request.session['cart'] = cart
    new_count = sum(v['quantity'] if isinstance(v, dict) else v for v in cart.values())
    request.session['cart_count'] = new_count
    request.session.modified = True

    new_total_cart = _get_cart_data(cart)

    return JsonResponse({
        'success': True,
        'cart_count': new_count,
        'item_count': current_qty,
        'total_cart': float(new_total_cart)
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_remove_from_cart(request):
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
    except Exception:
        data = {}

    item_key = data.get('item_key') or request.POST.get('item_key')
    if not item_key:
        return JsonResponse({'success': False, 'error': 'item_key required'}, status=400)

    cart = request.session.get('cart', {})
    if item_key in cart:
        del cart[item_key]

    request.session['cart'] = cart
    new_count = sum(v['quantity'] if isinstance(v, dict) else v for v in cart.values())
    request.session['cart_count'] = new_count
    request.session.modified = True

    new_total_cart = _get_cart_data(cart)

    return JsonResponse({'success': True, 'cart_count': new_count, 'total_cart': float(new_total_cart)})


@csrf_exempt
@require_http_methods(["POST"])
def api_checkout(request):
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
    except Exception:
        data = {}

    item_keys = data.get('items') or []
    if not item_keys:
        return JsonResponse({'success': False, 'error': 'no items provided'}, status=400)

    cart = request.session.get('cart', {})
    checkout_items = []
    total_price = 0

    for key in item_keys:
        if key in cart:
            try:
                parts = key.split('_')
                product_id = parts[0]
                size = parts[1] if len(parts) > 1 else 'N/A'
                quantity = cart[key]['quantity'] if isinstance(cart[key], dict) else cart[key]
                product = Product.objects.get(id=int(product_id))
                item_total = float(product.price) * int(quantity)
                total_price += item_total
                checkout_items.append({'item_key': key, 'product_id': product.id, 'quantity': quantity, 'size': size, 'total_price': item_total})
            except Exception:
                continue

    return JsonResponse({'success': True, 'items': checkout_items, 'total_price': float(total_price)})