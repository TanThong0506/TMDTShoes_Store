from django.contrib import admin
from django import forms
from .models import Order, OrderItem


class OrderItemInlineForm(forms.ModelForm):
    # Keep field visible but not required; value is always pulled from Product in clean().
    price = forms.DecimalField(required=False)

    class Meta:
        model = OrderItem
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        if product:
            cleaned_data['price'] = product.price
        return cleaned_data


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    form = OrderItemInlineForm
    autocomplete_fields = ['product']
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'full_name', 'phone', 'total_price', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    list_editable = ['status']
    search_fields = ['full_name', 'phone']
    readonly_fields = ['return_reason']
    inlines = [OrderItemInline]

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        order = form.instance
        total = 0
        for item in order.orderitem_set.all():
            if item.product_id and not item.price:
                item.price = item.product.price
                item.save(update_fields=['price'])
            total += int(item.price) * int(item.quantity)

        if order.total_price != total:
            order.total_price = total
            order.save(update_fields=['total_price'])
