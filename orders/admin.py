from django.contrib import admin
from .models import Order, OrderItem 

# 1. Khai báo cái Inline TRƯỚC
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] 
    extra = 0 

# 2. Khai báo Admin SAU và gọi Inline đã tạo ở trên vào
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'total_price', 'payment_method', 'created_at']
    list_filter = ['payment_method', 'created_at']
    search_fields = ['full_name', 'phone']
    
    # Bây giờ dòng này mới chạy được vì OrderItemInline đã tồn tại ở trên
    inlines = [OrderItemInline]