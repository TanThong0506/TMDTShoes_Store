from django.shortcuts import render, redirect
from django.contrib.auth.models import User
# BƯỚC 1: Mình đã thêm chữ 'logout' vào dòng import này
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


# HÀM XỬ LÝ ĐĂNG KÝ
def register_view(request):
    if request.method == 'POST':
        # 1. Lấy dữ liệu người dùng nhập từ form HTML
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password') or ''
        confirm_password = request.POST.get('confirm_password') or ''

        # 2. Kiểm tra dữ liệu
        if not username:
            messages.error(request, 'Tên đăng nhập không được để trống!')
            return redirect('register')

        if not email:
            messages.error(request, 'Email không được để trống!')
            return redirect('register')

        # validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Email không hợp lệ!')
            return redirect('register')

        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return redirect('register')

        # validate password strength using Django validators
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

        # 3. Tạo tài khoản và lưu vào Database
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect('login') # Đăng ký xong tự động chuyển sang trang đăng nhập

    # Nếu là request GET (vào trang bình thường) thì chỉ hiện giao diện
    return render(request, 'register.html')


# HÀM XỬ LÝ ĐĂNG NHẬP
def login_view(request):
    if request.method == 'POST':
        # 1. Lấy dữ liệu từ form
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''

        if not username or not password:
            messages.error(request, 'Vui lòng nhập cả tên đăng nhập và mật khẩu.')
            return render(request, 'login.html')

        # 2. Kiểm tra xem tài khoản có đúng không
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # 3. Đăng nhập thành công
            login(request, user)
            return redirect('home') # Chuyển hướng về trang chủ
        else:
            # 4. Đăng nhập thất bại
            messages.error(request, 'Sai tên đăng nhập hoặc mật khẩu!')

    return render(request, 'login.html')


# BƯỚC 2: THÊM HÀM ĐĂNG XUẤT VÀO CUỐI CÙNG
def logout_view(request):
    logout(request) # Lệnh này xóa phiên đăng nhập hiện tại
    return redirect('home') # Đá người dùng về trang chủ