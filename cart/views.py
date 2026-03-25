from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from products.models import Product
from django.contrib.humanize.templatetags.humanize import intcomma

# Hàm phụ trợ tính toán lại toàn bộ giỏ hàng để dùng chung cho các hàm update/remove
def _get_cart_data(cart):
    total = 0
    for item_key, quantity in cart.items():
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
    for item_key, quantity in cart.items():
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
        
        cart[item_key] = cart.get(item_key, 0) + quantity
        
        request.session['cart'] = cart
        new_count = sum(cart.values())
        request.session['cart_count'] = new_count
        request.session.modified = True
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'cart_count': new_count})
        return redirect('cart:cart_detail')
    return redirect('home')

def update_cart(request, item_key, action):
    cart = request.session.get('cart', {})
    item_total_html = "0"
    
    if item_key in cart:
        if action == 'increase':
            cart[item_key] += 1
        elif action == 'decrease':
            cart[item_key] -= 1
            if cart[item_key] <= 0:
                del cart[item_key]
        
        if item_key in cart:
            p_id = item_key.split('_')[0]
            product = Product.objects.get(id=int(p_id))
            item_total_html = intcomma(product.price * cart[item_key])

    request.session['cart'] = cart
    new_count = sum(cart.values())
    request.session['cart_count'] = new_count
    request.session.modified = True
    
    new_total_cart = _get_cart_data(cart)
    
    return JsonResponse({
        'success': True, 
        'cart_count': new_count,
        'item_count': cart.get(item_key, 0),
        'item_total': item_total_html,
        'total_cart': intcomma(new_total_cart)
    })

def remove_from_cart(request, item_key):
    cart = request.session.get('cart', {})
    if item_key in cart:
        del cart[item_key]
        
    request.session['cart'] = cart
    new_count = sum(cart.values())
    request.session['cart_count'] = new_count
    request.session.modified = True
    
    new_total_cart = _get_cart_data(cart)
    
    return JsonResponse({
        'success': True,
        'cart_count': new_count,
        'total_cart': intcomma(new_total_cart)
    })

# --- HÀM CHECKOUT ĐÃ ĐƯỢC SỬA LẠI CHUẨN ---
def checkout(request):
    cart = request.session.get('cart', {})
    item_keys_str = request.GET.get('items', '')
    
    if not item_keys_str:
        return redirect('cart:cart_detail')
    
    selected_keys = item_keys_str.split(',')
    checkout_items = []
    total_price = 0
    
    # Duyệt qua các key được chọn từ giao diện gửi lên
    for key in selected_keys:
        if key in cart:
            try:
                # Tách ID sản phẩm và Size từ item_key (ví dụ: "1_39")
                parts = key.split('_')
                product_id = parts[0]
                size = parts[1] if len(parts) > 1 else "N/A"
                
                # Lấy số lượng từ session
                quantity = cart[key]
                
                # Truy vấn sản phẩm từ DB để lấy giá và tên
                product = Product.objects.get(id=int(product_id))
                
                # Tính toán số tiền
                item_total = product.price * quantity
                total_price += item_total
                
                # Thêm vào danh sách hiển thị
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