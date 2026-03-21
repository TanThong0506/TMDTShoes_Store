
# TMDTShoes_Store
📦 Django + MySQL (XAMPP) Setup Guide
🎯 Mục tiêu

Hướng dẫn cấu hình Django kết nối với MySQL thông qua XAMPP và đồng bộ cơ sở dữ liệu bằng migration.

🧰 Yêu cầu hệ thống

Python ≥ 3.8

Django ≥ 3.x

XAMPP (MySQL + phpMyAdmin)

pip

🚀 1. Tạo Database trong XAMPP

Mở trình duyệt:

http://localhost/phpmyadmin

Tạo database mới:

shoe_store

Chọn:

Collation: utf8mb4_general_ci

⚙️ 2. Cài đặt MySQL Driver
Cách 1 (khuyến nghị):
pip install mysqlclient
Cách 2 (nếu lỗi):
pip install PyMySQL
🛠️ 3. Cấu hình Django (settings.py)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'shoe_store',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3307',
    }
}

🔧 4. Nếu dùng PyMySQL (fix lỗi)

Trong file __init__.py:

import pymysql
pymysql.install_as_MySQLdb()
🔄 5. Đồng bộ CSDL (Migration)
Tạo migration:
python manage.py makemigrations
Áp dụng vào database:
python manage.py migrate
✅ 6. Kiểm tra

Vào lại phpMyAdmin → database tmdt_shoes

Nếu thấy các bảng như:

auth_user

django_admin_log

yourapp_*

👉 Nghĩa là đã đồng bộ thành công 🎉

🔁 7. Khi thay đổi Model

Sau khi chỉnh sửa models.py:

python manage.py makemigrations
python manage.py migrate
⚠️ Lỗi thường gặp
❌ Không kết nối được MySQL

Kiểm tra XAMPP đã bật MySQL chưa

❌ Sai port

Thử đổi: cho phù hợp với cổng trên lap

'PORT': '3307'
❌ Access denied

Kiểm tra password MySQL trong XAMPP

❌ Không thấy bảng

Chưa chạy migrate

📤 8. Export / Import dữ liệu
Export:
python manage.py dumpdata > data.json
Import:
python manage.py loaddata data.json
🎯 Kết luận

XAMPP chỉ đóng vai trò MySQL Server

Django quản lý database qua:

makemigrations → migrate
👨‍💻 Tác giả
Thong

Project: TMDT Shoes Store

Backend: Django + MySQL
