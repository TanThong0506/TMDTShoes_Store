from django.contrib import admin
from .models import Product, ProductImage, Size, Category, Brand, Review, StorePolicy

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  
    verbose_name = "Ảnh phụ"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline] 
    list_display = ('name', 'price', 'stock', 'category', 'is_active') 
    list_editable = ('stock', 'price') 
    list_filter = ('category', 'is_active', 'brand')
    search_fields = ('name',)
    filter_horizontal = ('sizes',) 

    # Cấu hình hiển thị: Đã loại bỏ 2 ô chính sách cũ
    fieldsets = (
        ("Thông tin cơ bản", {
            'fields': ('name', 'brand', 'category', 'price', 'old_price', 'image', 'sizes')
        }),
        ("Quản lý kho hàng", {
            'fields': ('stock', 'is_active', 'stock_status')
        }),
        ("Nội dung mô tả sản phẩm", {
            'classes': ('collapse',), 
            'fields': ('description',),
        }),
    )

# Đăng ký mục Chính sách riêng biệt
@admin.register(StorePolicy)
class StorePolicyAdmin(admin.ModelAdmin):
    list_display = ('title',)
    def has_add_permission(self, request):
        return False if StorePolicy.objects.count() >= 1 else True

admin.site.register(Size)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Review)