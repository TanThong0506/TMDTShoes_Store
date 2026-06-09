from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Order, OrderItem, Coupon
from products.models import Product 
from cart.models import Cart, CartItem 
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)


def _extract_quantity(cart_value):
    if isinstance(cart_value, dict):
        return int(cart_value.get('quantity', 0) or 0)
    return int(cart_value or 0)

@login_required(login_url='login')
def checkout(request):
    # Lấy danh sách key sản phẩm từ URL (ví dụ: ?items=1_40,2_39)
    item_keys_str = request.GET.get('items', '')
    cart = request.session.get('cart', {})
    
    if not item_keys_str:
        messages.error(request, 'Giỏ hàng của bạn đang trống.')
        return redirect('cart:cart_detail')
    
    items_to_display = []
    total_price = 0
    errors = []
    
    for key in item_keys_str.split(','):
        if not key or key not in cart:
            continue
        
        try:
            quantity = _extract_quantity(cart[key])
            if quantity <= 0:
                errors.append(f'Sản phẩm có số lượng không hợp lệ')
                continue
            
            # Tách lấy ID từ key (ví dụ "1_39" -> lấy "1")
            product_id = key.split('_')[0]
            
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                errors.append(f'Sản phẩm không tồn tại')
                continue
            
            if not product.is_active:
                errors.append(f'Sản phẩm {product.name} không còn bán')
                continue
            
            size = key.split('_')[1] if '_' in key else 'N/A'
            from products.models import ProductVariant
            try:
                variant = ProductVariant.objects.get(product=product, size__value=size)
                stock_available = variant.stock
            except ProductVariant.DoesNotExist:
                stock_available = 0
            
            # Kiểm tra kho hàng
            if stock_available <= 0:
                errors.append(f'Sản phẩm {product.name} (Size {size}) hiện tại không có hàng')
                continue
            
            if quantity > stock_available:
                errors.append(f'Chỉ còn {stock_available} {product.name} (Size {size}) trong kho')
                continue
            
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
        
        except (ValueError, IndexError) as e:
            errors.append('Thông tin sản phẩm không hợp lệ')
            continue
    
    if errors:
        for error in errors:
            messages.warning(request, error)
    
    if not items_to_display:
        messages.error(request, 'Không có sản phẩm hợp lệ để thanh toán.')
        return redirect('cart:cart_detail')

    context = {
        'items': items_to_display,
        'total_price': total_price,
        'user_addresses': request.user.shipping_addresses.all(),
    }
    return render(request, 'checkout.html', context)

@login_required(login_url='login')
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
        
        # Validation for empty items
        if not item_keys_str:
            messages.error(request, "Vui lòng chọn ít nhất một sản phẩm để đặt hàng.")
            return redirect('cart:cart_detail')

        # Validation for full name
        if not full_name:
            messages.error(request, 'Vui lòng cung cấp họ và tên.')
            return redirect(f'/orders/checkout/?items={item_keys_str}')
        
        if len(full_name) > 200:
            messages.error(request, 'Họ và tên quá dài (tối đa 200 ký tự).')
            return redirect(f'/orders/checkout/?items={item_keys_str}')

        # Validation for phone
        if not phone:
            messages.error(request, 'Vui lòng cung cấp số điện thoại.')
            return redirect(f'/orders/checkout/?items={item_keys_str}')
        
        if not phone.isdigit():
            messages.error(request, 'Số điện thoại chỉ được chứa các chữ số.')
            return redirect(f'/orders/checkout/?items={item_keys_str}')
        
        if len(phone) < 9 or len(phone) > 11:
            messages.error(request, 'Số điện thoại không hợp lệ (9-11 chữ số).')
            return redirect(f'/orders/checkout/?items={item_keys_str}')

        # Validation for address
        if not address:
            messages.error(request, 'Vui lòng cung cấp địa chỉ giao hàng.')
            return redirect(f'/orders/checkout/?items={item_keys_str}')
        
        if len(address) > 1000:
            messages.error(request, 'Địa chỉ quá dài (tối đa 1000 ký tự).')
            return redirect(f'/orders/checkout/?items={item_keys_str}')

        # Validation for payment method
        allowed_payment_methods = {'COD', 'BANK', 'VNPAY'}
        if not payment_method:
            messages.error(request, 'Vui lòng chọn phương thức thanh toán.')
            return redirect(f'/orders/checkout/?items={item_keys_str}')
        
        if payment_method not in allowed_payment_methods:
            messages.error(request, 'Phương thức thanh toán không hợp lệ.')
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
        validation_errors = []
        
        for key in item_keys_str.split(','):
            if not key:
                continue
            
            if key not in cart_session:
                validation_errors.append(f'Sản phẩm không có trong giỏ hàng')
                continue
            
            try:
                quantity = _extract_quantity(cart_session[key])
                if quantity <= 0:
                    validation_errors.append(f'Số lượng sản phẩm không hợp lệ')
                    continue
                
                product_id = key.split('_')[0]
                size = key.split('_')[1] if '_' in key else 'N/A'
                
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    validation_errors.append(f'Sản phẩm không tồn tại')
                    continue
                
                if not product.is_active:
                    validation_errors.append(f'Sản phẩm {product.name} không còn bán')
                    continue
                
                size = key.split('_')[1] if '_' in key else 'N/A'
                from products.models import ProductVariant
                try:
                    variant = ProductVariant.objects.get(product=product, size__value=size)
                    stock_available = variant.stock
                except ProductVariant.DoesNotExist:
                    stock_available = 0
                
                # Kiểm tra kho hàng
                if stock_available <= 0:
                    validation_errors.append(f'Sản phẩm {product.name} (Size {size}) hiện tại không có hàng')
                    continue
                
                if quantity > stock_available:
                    validation_errors.append(f'Chỉ còn {stock_available} {product.name} (Size {size}) trong kho')
                    continue
                
                # Trừ tồn kho Variant
                variant.stock -= quantity
                variant.save()
                
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
            
            except (ValueError, IndexError) as e:
                validation_errors.append(f'Thông tin sản phẩm không hợp lệ')
                continue

        # Nếu không có items hợp lệ, xóa order
        if not keys_to_delete:
            order.delete()
            for error in validation_errors:
                messages.error(request, error)
            if not validation_errors:
                messages.error(request, 'Không có sản phẩm nào hợp lệ để đặt hàng.')
            return redirect('cart:cart_detail')

        # Xử lý Mã giảm giá
        coupon_code = (request.POST.get('coupon_code') or '').strip()
        discount_amount = 0
        if coupon_code:
            coupon = Coupon.objects.filter(code__iexact=coupon_code).first()
            if coupon and coupon.is_valid():
                discount_amount = coupon.discount_amount
                order.coupon = coupon
                order.discount_amount = discount_amount

        # Đảm bảo tổng tiền không âm
        final_total = max(0, current_total - discount_amount)
        order.total_price = final_total
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
                logger.warning("Lỗi DB khi xóa cart items sau khi tạo đơn: %s", e)
        
        # Hiển thị warning nếu có lỗi partial
        for error in validation_errors:
            messages.warning(request, error)
        
        # Show success message
        if len(keys_to_delete) > 0:
            messages.success(request, f'Đơn hàng được tạo thành công với {len(keys_to_delete)} sản phẩm!')
        
        # ----------------------------------------------
        
        request.session['last_order_id'] = order.id

        if payment_method == 'VNPAY':
            from .vnpay_utils import VNPay
            from django.urls import reverse
            vnp = VNPay(
                tmn_code='S7OQQ9M9', # Mã Sandbox mẫu
                hash_secret='QPVITQYRYEGBGGBVUXUXBOMJTZTOWMOC', # Secret mẫu
                return_url=request.build_absolute_uri(reverse('orders:vnpay_return')),
                vnpay_url='https://sandbox.vnpayment.vn/paymentv2/vpcpay.html'
            )
            payment_url = vnp.get_payment_url(
                order_id=order.id,
                amount=final_total,
                order_desc=f"Thanh toan don hang {order.id}",
                ip_address=request.META.get('REMOTE_ADDR', '127.0.0.1')
            )
            return redirect(payment_url)

        return redirect('orders:order_success')
    
    return redirect('orders:checkout')

@login_required(login_url='login')
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

@login_required(login_url='login')
def apply_coupon(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            code = data.get('code', '').strip()
            if not code:
                return JsonResponse({'success': False, 'message': 'Vui lòng nhập mã giảm giá'})
            
            coupon = Coupon.objects.filter(code__iexact=code).first()
            if coupon and coupon.is_valid():
                return JsonResponse({
                    'success': True, 
                    'discount_amount': float(coupon.discount_amount),
                    'message': f'Áp dụng thành công mã giảm {coupon.discount_amount} VND'
                })
            else:
                return JsonResponse({'success': False, 'message': 'Mã giảm giá không hợp lệ hoặc đã hết hạn'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Lỗi xử lý mã giảm giá'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required(login_url='login')
def vnpay_return(request):
    from .vnpay_utils import VNPay
    vnp = VNPay(
        tmn_code='S7OQQ9M9',
        hash_secret='QPVITQYRYEGBGGBVUXUXBOMJTZTOWMOC',
        return_url='',
        vnpay_url=''
    )
    
    if vnp.validate_response(request.GET):
        order_id = request.GET.get('vnp_TxnRef')
        vnp_ResponseCode = request.GET.get('vnp_ResponseCode')
        
        try:
            order = Order.objects.get(id=order_id)
            order.transaction_id = request.GET.get('vnp_TransactionNo')
            if vnp_ResponseCode == '00':
                order.payment_status = 'Success'
                order.status = 'Completed'
                order.save()
                messages.success(request, 'Thanh toán VNPay thành công!')
            else:
                order.payment_status = 'Failed'
                order.status = 'Cancelled'
                order.save()
                messages.error(request, 'Thanh toán VNPay thất bại hoặc bị hủy.')
        except Order.DoesNotExist:
            messages.error(request, 'Đơn hàng không tồn tại.')
    else:
        messages.error(request, 'Xác thực VNPay thất bại. Chữ ký không hợp lệ.')
        
    return redirect('orders:order_success')