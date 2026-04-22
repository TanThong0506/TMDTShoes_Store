from django.contrib import admin
from django import forms  # <-- Bắt buộc phải import forms
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, CharField
from django.db.models.functions import Cast, Substr
from collections import defaultdict
from django.urls import path
from django.template.response import TemplateResponse
from .models import Product, ProductImage, Size, Category, Brand, Review, StorePolicy, SalesReport
from .models import Sale
from orders.models import OrderItem

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


class SalesReportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/products/salesreport/change_list.html'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'revenue-report/',
                self.admin_site.admin_view(self.revenue_report_view),
                name='products_salesreport_revenue_report',
            ),
        ]
        return custom_urls + urls

    def revenue_report_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
            title='Báo cáo doanh thu',
            sales_chart_data=self._build_revenue_context(),
            opts=self.model._meta,
        )
        return TemplateResponse(request, 'admin/products/salesreport/revenue_report.html', context)

    def _build_revenue_context(self):
        completed_statuses = ['Completed', 'Đã thanh toán', 'Đã thanh toán/Hoàn thành', 'Hoàn thành']
        base_queryset = OrderItem.objects.filter(order__status__in=completed_statuses)
        month_key_expr = Substr(Cast('order__created_at', output_field=CharField()), 1, 7)

        revenue_expr = ExpressionWrapper(
            F('price') * F('quantity'),
            output_field=DecimalField(max_digits=18, decimal_places=0)
        )

        monthly_totals = (
            base_queryset
            .annotate(month_key=month_key_expr)
            .values('month_key')
            .annotate(total_revenue=Sum(revenue_expr), total_quantity=Sum('quantity'))
            .order_by('month_key')
        )

        product_totals = (
            base_queryset
            .annotate(month_key=month_key_expr)
            .values('month_key', 'product_id', 'product__name')
            .annotate(total_revenue=Sum(revenue_expr), total_quantity=Sum('quantity'))
            .order_by('month_key', '-total_revenue', 'product__name')
        )

        size_totals = (
            base_queryset
            .annotate(month_key=month_key_expr)
            .values('month_key', 'product_id', 'size')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('month_key', 'product_id', 'size')
        )

        month_products = defaultdict(list)
        month_product_index = defaultdict(dict)

        for row in product_totals:
            month_key = row.get('month_key')
            if not month_key:
                continue
            product_payload = {
                'product_id': row['product_id'],
                'product_name': row['product__name'],
                'quantity': int(row['total_quantity'] or 0),
                'revenue': int(row['total_revenue'] or 0),
                'sizes': [],
            }
            month_products[month_key].append(product_payload)
            month_product_index[month_key][row['product_id']] = product_payload

        for row in size_totals:
            month_key = row.get('month_key')
            if not month_key:
                continue
            product_payload = month_product_index.get(month_key, {}).get(row['product_id'])
            if not product_payload:
                continue
            product_payload['sizes'].append({
                'size': row['size'] or 'N/A',
                'quantity': int(row['total_quantity'] or 0),
            })

        months_payload = []
        for row in monthly_totals:
            month_key = row.get('month_key')
            if not month_key:
                continue
            year, month = month_key.split('-')
            months_payload.append({
                'key': month_key,
                'label': f"{month}/{year}",
                'quantity': int(row['total_quantity'] or 0),
                'revenue': int(row['total_revenue'] or 0),
            })

        return {
            'months': months_payload,
            'month_products': dict(month_products),
        }

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['sales_chart_data'] = self._build_revenue_context()
        return super().changelist_view(request, extra_context=extra_context)

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


@admin.register(SalesReport)
class SalesReportProxyAdmin(SalesReportAdmin):
    pass