from django.contrib import admin
from .models import Product, ProductImage, Size, Category, Brand, Review

# Tạo khung để đăng ảnh phụ ngay trong trang sửa Product
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Hiện sẵn 3 ô để chọn ảnh phụ
    verbose_name = "Ảnh phụ"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Thêm mục đăng ảnh phụ vào trang sửa sản phẩm
    inlines = [ProductImageInline] 
    
    # Hiển thị thông tin cơ bản ngoài danh sách
    list_display = ['name', 'price', 'brand', 'stock_status']
    
    # Giúp giao diện chọn Size (ManyToManyField) dễ nhìn hơn
    filter_horizontal = ['sizes'] 

# Đăng ký các model còn lại để quản lý trong Admin
admin.site.register(Size)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Review)