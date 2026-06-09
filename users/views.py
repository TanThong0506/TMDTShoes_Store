from django.shortcuts import render, redirect
from django.contrib.auth.models import User
# BƯỚC 1: Giữ nguyên các import cũ của bạn
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
import logging

# THÊM MỚI: Import thêm thư viện gửi mail và Model OTP
from django.core.mail import send_mail
from .models import PasswordResetOTP, UserProfile, ShippingAddress
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from orders.models import Order


logger = logging.getLogger(__name__)

import re
import uuid

# HÀM XỬ LÝ ĐĂNG KÝ
def register_view(request):
    if request.method == 'POST':
        full_name = (request.POST.get('full_name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        password = request.POST.get('password') or ''
        confirm_password = request.POST.get('confirm_password') or ''

        # TC_02: Trống tất cả các trường
        if not full_name and not email and not phone and not password and not confirm_password:
            messages.error(request, 'Vui lòng nhập đầy đủ ở tất cả các trường.')
            return render(request, 'register.html')

        # TC_03: Bỏ trống trường Họ tên
        if not full_name:
            messages.error(request, 'Vui lòng nhập họ tên')
            return render(request, 'register.html')
            
        # TC_04: Bỏ trống trường Email
        if not email:
            messages.error(request, 'Vui lòng nhập email')
            return render(request, 'register.html')

        # Thêm check cho SĐT
        if not phone:
            messages.error(request, 'Vui lòng nhập số điện thoại')
            return render(request, 'register.html')

        # TC_05: Bỏ trống trường Mật khẩu
        if not password:
            messages.error(request, 'Vui lòng nhập mật khẩu')
            return render(request, 'register.html')

        # TC_06: Bỏ trống trường Xác nhận mật khẩu
        if not confirm_password:
            messages.error(request, 'Vui lòng xác nhận mật khẩu')
            return render(request, 'register.html')

        # TC_15: Tên chứa ký tự đặc biệt
        if re.search(r'[^a-zA-ZÀ-ỹ\s]', full_name):
            messages.error(request, 'Họ tên không được chứa ký tự đặc biệt')
            return render(request, 'register.html')

        # TC_17: Giới hạn độ dài trường Họ tên
        if len(full_name) > 50:
            messages.error(request, 'Họ tên vượt quá 50 ký tự')
            return render(request, 'register.html')

        # TC_07, TC_08, TC_19: Định dạng Email không hợp lệ
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            messages.error(request, 'Email không đúng định dạng')
            return render(request, 'register.html')

        # TC_09: Email đã tồn tại trong hệ thống
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email này đã được sử dụng')
            return render(request, 'register.html')

        # TC_10: Mật khẩu và Xác nhận mật khẩu không khớp
        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp')
            return render(request, 'register.html')

        # TC_11: Mật khẩu quá ngắn
        if len(password) < 8:
            messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự')
            return render(request, 'register.html')

        # TC_12: Mật khẩu thiếu ký tự đặc biệt/số (và chữ hoa theo yêu cầu TC)
        if not (re.search(r'[A-Z]', password) and re.search(r'[0-9]', password) and re.search(r'[^A-Za-z0-9]', password)):
            messages.error(request, 'Mật khẩu phải chứa chữ hoa, số và ký tự đặc biệt')
            return render(request, 'register.html')

        # TC_13: Số điện thoại chứa chữ cái
        if not phone.isdigit():
            messages.error(request, 'Số điện thoại chỉ được chứa chữ số')
            return render(request, 'register.html')

        # TC_14: Số điện thoại quá ngắn (chuẩn VN là 10 số)
        if len(phone) < 10:
            messages.error(request, 'Số điện thoại không hợp lệ')
            return render(request, 'register.html')

        # TC_18: Đăng ký với SĐT đã tồn tại
        if UserProfile.objects.filter(phone=phone).exists():
            messages.error(request, 'Số điện thoại đã được đăng ký')
            return render(request, 'register.html')

        # TC_01: Đăng ký thành công với dữ liệu hợp lệ
        parts = full_name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        # Tạo username duy nhất từ email và UUID (chống trùng lặp cho User model của Django)
        base_username = email.split('@')[0]
        username = f"{base_username}_{str(uuid.uuid4())[:8]}"

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        UserProfile.objects.create(user=user, phone=phone)
        
        messages.success(request, 'Đăng ký thành công.')
        return redirect('login')

    return render(request, 'register.html')


# HÀM XỬ LÝ ĐĂNG NHẬP (GIỮ NGUYÊN)
def login_view(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''

        if not username or not password:
            messages.error(request, 'Vui lòng nhập cả tên đăng nhập và mật khẩu.')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home') 
        else:
            messages.error(request, 'Sai tên đăng nhập hoặc mật khẩu!')

    return render(request, 'login.html')


# HÀM ĐĂNG XUẤT (GIỮ NGUYÊN)
def logout_view(request):
    logout(request) 
    return redirect('home') 


# ============================================================
# PHẦN THÊM MỚI: LOGIC QUÊN MẬT KHẨU (OTP)
# ============================================================

# 1. Nhập email và gửi OTP
def forgot_password_view(request):
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        
        if user:
            # Lấy hoặc tạo mới bản ghi OTP cho người dùng
            otp_obj, created = PasswordResetOTP.objects.get_or_create(user=user)
            otp_obj.generate_otp()
            
            # Gửi mail thực tế
            subject = '[Shoestore] Mã OTP đặt lại mật khẩu'
            message = f'Chào {user.username}, mã xác thực của bạn là: {otp_obj.otp}. Vui lòng không cung cấp mã này cho người khác.'
            
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
                request.session['reset_email'] = user.email # Lưu email vào phiên làm việc
                request.session.pop('debug_reset_otp', None)
                if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                    request.session['debug_reset_otp'] = otp_obj.otp
                    messages.warning(request, 'Hệ thống đang chạy local: OTP được in trong terminal chạy server, không gửi về email thật.')
                return redirect('verify_otp')
            except Exception as e:
                logger.exception('Send OTP email failed: %s', e)
                if settings.DEBUG:
                    # Fallback cho môi trường dev để vẫn test được luồng quên mật khẩu.
                    request.session['reset_email'] = email
                    request.session['debug_reset_otp'] = otp_obj.otp
                    messages.warning(request, f'Không gửi được email. Mã OTP test của bạn là: {otp_obj.otp}')
                    return redirect('verify_otp')
                messages.error(request, 'Lỗi hệ thống không thể gửi mail. Vui lòng thử lại sau!')
        else:
            messages.error(request, 'Email này chưa được đăng ký trong hệ thống!')
            
    return render(request, 'users/forgot_password.html')


# 2. Xác nhận OTP
def verify_otp_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    user = User.objects.filter(email=email).first()
    if not user:
        request.session.pop('reset_email', None)
        request.session.pop('debug_reset_otp', None)
        messages.error(request, 'Phiên đặt lại mật khẩu đã hết hạn. Vui lòng thử lại.')
        return redirect('forgot_password')

    if request.method == 'POST':
        otp_input = (request.POST.get('otp') or '').strip()
        if not otp_input.isdigit() or len(otp_input) != 6:
            messages.error(request, 'OTP phải gồm đúng 6 chữ số!')
            return render(request, 'users/verify_otp.html')

        # Kiểm tra mã OTP trong database
        otp_record = PasswordResetOTP.objects.filter(user=user, otp=otp_input).first()

        if otp_record:
            return redirect('reset_password')
        else:
            messages.error(request, 'Mã OTP bạn nhập không chính xác!')
            
    return render(request, 'users/verify_otp.html')


# 3. Thiết lập mật khẩu mới
def reset_password_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            try:
                # Kiểm tra độ mạnh mật khẩu mới
                validate_password(password)
                
                user = User.objects.get(email=email)
                user.set_password(password) # Mã hóa mật khẩu mới
                user.save()
                
                # Xóa OTP đã dùng và dọn dẹp session
                PasswordResetOTP.objects.filter(user=user).delete()
                del request.session['reset_email']
                request.session.pop('debug_reset_otp', None)
                
                messages.success(request, 'Đặt lại mật khẩu thành công! Hãy đăng nhập với mật khẩu mới.')
                return redirect('login')
            except ValidationError as e:
                messages.error(request, ' '.join(e.messages))
        else:
            messages.error(request, 'Mật khẩu xác nhận không trùng khớp!')

    return render(request, 'users/reset_password.html')


# ============================================================
# PHẦN THÊM MỚI: THÔNG TIN CÁ NHÂN (PROFILE)
# ============================================================
@login_required(login_url='login')
def profile_view(request):
    user = request.user
    # Lấy hoặc tạo Profile cho user nếu chưa có
    profile, created = UserProfile.objects.get_or_create(user=user)

    # TỰ ĐỘNG ĐIỀN DỮ LIỆU TỪ LSQĐ NẾU PROFILE TRỐNG
    if not profile.phone or not profile.address or not user.first_name:
        from orders.models import Order # Import model Order
        last_order = Order.objects.filter(user=user).order_by('-created_at').first()
        if last_order:
            if not profile.phone and last_order.phone:
                profile.phone = last_order.phone
            if not profile.address and last_order.address:
                profile.address = last_order.address
            profile.save()
            
            if not user.first_name and last_order.full_name:
                parts = last_order.full_name.split(' ', 1)
                user.first_name = parts[0]
                if len(parts) > 1:
                    user.last_name = parts[1]
                user.save()

    if request.method == 'POST':
        # Cập nhật thông tin cơ bản
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        
        # Cập nhật thông tin profile
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        # Xử lý cập nhật mật khẩu (nếu có yêu cầu đổi)
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        has_error = False

        # Kiểm tra email trùng lặp (nếu đổi email)
        if email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'Email này đã được sử dụng bởi tài khoản khác!')
                has_error = True
            else:
                try:
                    validate_email(email)
                    user.email = email
                except ValidationError:
                    messages.error(request, 'Email không hợp lệ!')
                    has_error = True

        if not has_error:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            profile.phone = phone
            profile.address = address
            profile.save()

            # Nếu người dùng có nhập mật khẩu cũ, coi như họ muốn đổi mật khẩu
            if old_password:
                if user.check_password(old_password):
                    if new_password and new_password == confirm_password:
                        try:
                            # Kiểm tra độ mạnh của mật khẩu mới
                            validate_password(new_password, user)
                            user.set_password(new_password)
                            user.save()
                            # Giữ trạng thái đăng nhập sau khi đổi mật khẩu
                            update_session_auth_hash(request, user)
                            messages.success(request, 'Cập nhật thông tin và mật khẩu thành công!')
                        except ValidationError as e:
                            messages.error(request, ' '.join(e.messages))
                    else:
                        messages.error(request, 'Mật khẩu mới và mật khẩu xác nhận không trùng khớp hoặc bị trống!')
                else:
                    messages.error(request, 'Mật khẩu cũ không chính xác!')
            else:
                messages.success(request, 'Cập nhật thông tin cá nhân thành công!')

        return redirect('profile')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    addresses = request.user.shipping_addresses.all()
    wishlist_count = request.user.wishlists.count() if hasattr(request.user, 'wishlists') else 0

    context = {
        'user': user,
        'profile': profile,
        'orders': orders,
        'addresses': addresses,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'users/profile.html', context)

@login_required(login_url='login')
def add_address(request):
    if request.method == 'POST':
        # Limit to 5 addresses
        if request.user.shipping_addresses.count() >= 5:
            messages.error(request, 'Bạn chỉ được lưu tối đa 5 địa chỉ.')
            return redirect('profile')
            
        label = request.POST.get('label', 'Nhà')
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        
        is_default = request.POST.get('is_default') == 'on'
        
        if not full_name or not phone or not address:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin địa chỉ.')
            return redirect('profile')
            
        if is_default:
            request.user.shipping_addresses.update(is_default=False)
            
        is_first = request.user.shipping_addresses.count() == 0
            
        ShippingAddress.objects.create(
            user=request.user,
            label=label,
            full_name=full_name,
            phone=phone,
            address=address,
            is_default=is_default or is_first
        )
        messages.success(request, 'Thêm địa chỉ thành công.')
    return redirect('profile')

@login_required(login_url='login')
def delete_address(request, address_id):
    if request.method == 'POST':
        address = ShippingAddress.objects.filter(id=address_id, user=request.user).first()
        if address:
            was_default = address.is_default
            address.delete()
            if was_default:
                new_default = request.user.shipping_addresses.first()
                if new_default:
                    new_default.is_default = True
                    new_default.save()
            messages.success(request, 'Đã xóa địa chỉ.')
    return redirect('profile')

@login_required(login_url='login')
def set_default_address(request, address_id):
    if request.method == 'POST':
        address = ShippingAddress.objects.filter(id=address_id, user=request.user).first()
        if address:
            request.user.shipping_addresses.update(is_default=False)
            address.is_default = True
            address.save()
            messages.success(request, 'Đã cập nhật địa chỉ mặc định.')
    return redirect('profile')