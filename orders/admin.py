from django.contrib import admin
from .models import Order, OrderItem 

# 1. Khai báo cái Inline TRƯỚC
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] 
    extra = 0 

# 2. Khai báo Admin SAU và gọi Inline đã tạo ở trên vào
# orders/admin.py

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Thêm 'status' vào danh sách hiển thị
    list_display = ['id', 'status', 'full_name', 'phone', 'total_price', 'payment_method', 'created_at']
    
    # Thêm 'status' vào bộ lọc để dễ quản lý đơn hàng theo trạng thái
    list_filter = ['status', 'payment_method', 'created_at']
    
    # Giúp bạn đổi trạng thái ngay tại màn hình danh sách mà không cần bấm vào chi tiết đơn
    list_editable = ['status'] 
    
    search_fields = ['full_name', 'phone']
    inlines = [OrderItemInline]