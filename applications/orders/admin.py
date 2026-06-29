from django.contrib import admin
from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'total_price', 'status', 'payment_status', 'is_paid', 'created_at')
    list_filter = ('status', 'payment_status', 'is_paid', 'created_at')
    search_fields = ('user__username', 'phone', 'address', 'razorpay_order_id', 'razorpay_payment_id')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'food_item', 'quantity', 'price')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'user', 'amount', 'currency', 'gateway', 'status', 'paid_at', 'created_at')
    list_filter = ('gateway', 'status', 'currency', 'created_at', 'paid_at')
    search_fields = ('order__id', 'user__username', 'gateway_order_id', 'gateway_payment_id')
    readonly_fields = ('created_at', 'updated_at')
