from django.contrib import admin
from django import forms  # <-- Bắt buộc phải import forms
from .models import Product, ProductImage, Size, Category, Brand, Review, StorePolicy
from .models import Sale

# --- 1. TẠO FORM ẢO CHO ADMIN ĐỂ THÊM Ô % GIẢM GIÁ ---
class ProductAdminForm(forms.ModelForm):
    discount_percent = forms.IntegerField(
        required=False,
        label="Phần trăm giảm (%)",
        help_text="Mặc định tự tính % từ giá tiền. Bấm nút bên dưới để chuyển sang tự nhập %.",
        widget=forms.NumberInput(attrs={'readonly': 'readonly', 'style': 'background-color: #f0f0f0;'})
    )

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tự động tính % hiển thị ra ô khi vừa mở sản phẩm (đã có sẵn giá) lên
        if self.instance and self.instance.pk and self.instance.old_price and self.instance.price:
            if self.instance.old_price > self.instance.price:
                percent = ((self.instance.old_price - self.instance.price) / self.instance.old_price) * 100
                self.initial['discount_percent'] = round(percent)


# --- 2. CẬP NHẬT PRODUCT ADMIN ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  
    verbose_name = "Ảnh phụ"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Khai báo sử dụng Form ảo vừa tạo
    form = ProductAdminForm
    
    # Giao diện có chứa mã JavaScript đổi % và giá tiền
    change_form_template = 'admin/product_change_form.html'

    inlines = [ProductImageInline] 
    list_display = ('name', 'price', 'stock', 'display_categories', 'is_active') 
    list_editable = ('stock', 'price') 
    list_filter = ('category', 'is_active', 'brand')
    search_fields = ('name',)
    filter_horizontal = ('sizes', 'category') 

    # Cấu hình hiển thị
    fieldsets = (
        ("Thông tin cơ bản", {
            # ĐÃ SỬA: Thêm 'discount_percent' vào ngay sau giá
            'fields': ('name', 'brand', 'category', 'old_price', 'price', 'discount_percent', 'image', 'sizes')
        }),
        ("Quản lý kho hàng", {
            'fields': ('stock', 'is_active', 'stock_status')
        }),
        ("Nội dung mô tả sản phẩm", {
            'classes': ('collapse',), 
            'fields': ('description',),
        }),
    )

    def display_categories(self, obj):
        return ", ".join([cat.name for cat in obj.category.all()])
    display_categories.short_description = 'Loại sản phẩm'

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
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'active')
    list_filter = ('active',)
    filter_horizontal = ('products',)
    search_fields = ('title',)