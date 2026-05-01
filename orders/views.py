from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Order, OrderItem
from products.models import Product 
from cart.models import Cart, CartItem 


def _extract_quantity(cart_value):
    if isinstance(cart_value, dict):
        return int(cart_value.get('quantity', 0) or 0)
    return int(cart_value or 0)

def checkout(request):
    # Lấy danh sách key sản phẩm từ URL (ví dụ: ?items=1_40,2_39)
    item_keys_str = request.GET.get('items', '')
    cart = request.session.get('cart', {})
    
    items_to_display = []
    total_price = 0
    
    if item_keys_str:
        for key in item_keys_str.split(','):
            if key in cart:
                quantity = _extract_quantity(cart[key])
                if quantity <= 0:
                    continue
                # Tách lấy ID từ key (ví dụ "1_39" -> lấy "1")
                product_id = key.split('_')[0]
                product = get_object_or_404(Product, id=product_id)
                size = key.split('_')[1] if '_' in key else 'N/A'
                
                line_total = int(product.price) * quantity
                
                display_item = {
                    'item_key': key,
                    'product': product,
                    'quantity': quantity,
                    'size': size,
                    'price': product.price,
                    'total_price': line_total
                }
                total_price += line_total
                items_to_display.append(display_item)

    context = {
        'items': items_to_display,
        'total_price': total_price,
    }
    return render(request, 'checkout.html', context)

def order_create(request):
    if request.method == 'POST':
        full_name = (request.POST.get('full_name') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        address = (request.POST.get('address') or '').strip()
        payment_method = (request.POST.get('payment_method') or '').strip()
        selected_items = (request.POST.get('selected_items') or '').strip()
        
        # Ưu tiên danh sách item từ POST, fallback về query string để tương thích cũ
        item_keys_str = selected_items or request.GET.get('items', '')
        cart_session = request.session.get('cart', {})
        
        if not item_keys_str:
            messages.error(request, "Giỏ hàng của bạn đang trống.")
            return redirect('cart:cart_detail')

        # Basic input validation
        if not full_name or not phone:
            messages.error(request, 'Vui lòng cung cấp đầy đủ họ tên và số điện thoại.')
            return redirect(f'/orders/checkout/?items={item_keys_str}')

        if len(full_name) > 200 or len(address) > 1000:
            messages.error(request, 'Thông tin quá dài, vui lòng kiểm tra lại.')
            return redirect(f'/orders/checkout/?items={item_keys_str}')

        if not phone.isdigit() or len(phone) < 6:
            messages.error(request, 'Số điện thoại không hợp lệ.')
            return redirect(f'/orders/checkout/?items={item_keys_str}')

        allowed_payment_methods = {'COD', 'BANK'}
        if payment_method not in allowed_payment_methods:
            messages.error(request, 'Phương thức thanh toán không hợp lệ.')
            return redirect(f'/orders/checkout/?items={item_keys_str}')

        if not address:
            messages.error(request, 'Vui lòng cung cấp địa chỉ giao hàng.')
            return redirect(f'/orders/checkout/?items={item_keys_str}')

        # 1. Tạo đơn hàng
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name, 
            phone=phone, 
            address=address,
            payment_method=payment_method, 
            total_price=0 
        )
        
        current_total = 0
        keys_to_delete = []
        
        for key in item_keys_str.split(','):
            if key in cart_session:
                quantity = _extract_quantity(cart_session[key])
                if quantity <= 0:
                    continue
                product_id = key.split('_')[0]
                size = key.split('_')[1] if '_' in key else 'N/A'
                
                product = get_object_or_404(Product, id=product_id)
                line_total = int(product.price) * quantity
                current_total += line_total
                
                OrderItem.objects.create(
                    order=order, 
                    product=product,
                    price=product.price,
                    quantity=quantity,
                    size=size
                )
                keys_to_delete.append(key)

        order.total_price = current_total
        order.save()
        
        # --- ĐOẠN RESET GIỎ HÀNG VÀ CẬP NHẬT SỐ LƯỢNG ---
        
        # A. Xóa các item đã mua trong Session
        for key in keys_to_delete:
            if key in cart_session:
                del cart_session[key]
        
        # B. CẬP NHẬT LẠI CON SỐ TRÊN HEADER (Dòng quan trọng nhất)
        # Tính tổng số lượng của những sản phẩm CÒN LẠI trong giỏ
        request.session['cart'] = cart_session
        request.session['cart_count'] = sum(_extract_quantity(v) for v in cart_session.values()) if cart_session else 0
        request.session.modified = True

        # C. Xóa trong Database (Sử dụng ID để né lỗi cấu trúc bảng)
        if request.user.is_authenticated:
            try:
                cart_obj = Cart.objects.filter(user=request.user).first()
                if cart_obj:
                    # Chỉ xóa những item mà user vừa đặt hàng thành công trong DB
                    # Hoặc xóa hết item của user đó trong DB cho sạch
                    CartItem.objects.filter(cart=cart_obj).delete()
            except Exception as e:
                print(f"Lỗi DB nhưng đơn hàng vẫn tạo xong: {e}")
        
        # ----------------------------------------------
        
        request.session['last_order_id'] = order.id
        return redirect('orders:order_success')
    
    return redirect('orders:checkout')

def order_success(request):
    # 1. Sửa lại tên key cho khớp với hàm order_create (last_order_id)
    order_id = request.session.get('last_order_id')
    
    order = None
    if order_id:
        order = Order.objects.filter(id=order_id).first()
    
    # 2. Nếu không thấy trong session, lấy đơn mới nhất của chính User đó
    if not order:
        if request.user.is_authenticated:
            order = Order.objects.filter(user=request.user).order_by('-created_at').first()
        else:
            order = Order.objects.order_by('-created_at').first()

    if not order:
        return redirect('products:product_list')

    # 3. Trả về template (Đảm bảo file order_success.html của bạn có đoạn Script tự F5)
    return render(request, 'order_success.html', {'order': order})