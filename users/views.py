from django.shortcuts import render, redirect
from django.contrib.auth.models import User
# BƯỚC 1: Giữ nguyên các import cũ của bạn
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

# THÊM MỚI: Import thêm thư viện gửi mail và Model OTP
from django.core.mail import send_mail
from .models import PasswordResetOTP 

# HÀM XỬ LÝ ĐĂNG KÝ (GIỮ NGUYÊN)
def register_view(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''
        confirm_password = request.POST.get('confirm_password') or ''

        if not username:
            messages.error(request, 'Tên đăng nhập không được để trống!')
            return redirect('register')

        if not email:
            messages.error(request, 'Email không được để trống!')
            return redirect('register')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Email không hợp lệ!')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return redirect('register')

        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, ' '.join(e.messages))
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại!')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email này đã được sử dụng!')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
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
        email = (request.POST.get('email') or '').strip()
        user = User.objects.filter(email=email).first()
        
        if user:
            # Lấy hoặc tạo mới bản ghi OTP cho người dùng
            otp_obj, created = PasswordResetOTP.objects.get_or_create(user=user)
            otp_obj.generate_otp()
            
            # Gửi mail thực tế
            subject = '[Shoestore] Mã OTP đặt lại mật khẩu'
            message = f'Chào {user.username}, mã xác thực của bạn là: {otp_obj.otp}. Vui lòng không cung cấp mã này cho người khác.'
            
            try:
                send_mail(subject, message, 'noreply@shoestore.com', [email])
                request.session['reset_email'] = email # Lưu email vào phiên làm việc
                return redirect('verify_otp')
            except Exception as e:
                messages.error(request, 'Lỗi hệ thống không thể gửi mail. Vui lòng thử lại sau!')
        else:
            messages.error(request, 'Email này chưa được đăng ký trong hệ thống!')
            
    return render(request, 'users/forgot_password.html')


# 2. Xác nhận OTP
def verify_otp_view(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        user = User.objects.get(email=email)
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
                
                messages.success(request, 'Đặt lại mật khẩu thành công! Hãy đăng nhập với mật khẩu mới.')
                return redirect('login')
            except ValidationError as e:
                messages.error(request, ' '.join(e.messages))
        else:
            messages.error(request, 'Mật khẩu xác nhận không trùng khớp!')

    return render(request, 'users/reset_password.html')