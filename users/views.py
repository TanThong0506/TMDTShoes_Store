from django.shortcuts import render, redirect
from django.contrib.auth.models import User
# BƯỚC 1: Mình đã thêm chữ 'logout' vào dòng import này
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages


# HÀM XỬ LÝ ĐĂNG KÝ
def register_view(request):
    if request.method == 'POST':
        # 1. Lấy dữ liệu người dùng nhập từ form HTML
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 2. Kiểm tra dữ liệu
        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại!')
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
        username = request.POST.get('username')
        password = request.POST.get('password')

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