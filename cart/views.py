from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from products.models import Product
from django.contrib.humanize.templatetags.humanize import intcomma

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
    for item_key, item_val in cart.items():
        quantity = item_val['quantity'] if isinstance(item_val, dict) else item_val
        try:
            parts = item_key.split('_')
            p_id = parts[0]
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
    return render(request, 'cart.html', {'items': items, 'total': total})

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
                
                # Trích xuất số lượng an toàn
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

    context = {
        'items': checkout_items,
        'total_price': total_price,
    }
    return render(request, 'checkout.html', context)