from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from applications.restaurants.models import FoodItem


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        PREPARING = "Preparing", "Preparing"
        OUT_FOR_DELIVERY = "Out for Delivery", "Out for Delivery"
        DELIVERED = "Delivered", "Delivered"
        CANCELLED = "Cancelled", "Cancelled"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="orders")
    address = models.TextField()
    phone = models.CharField(max_length=15)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=30,choices=Status.choices,default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    razorpay_order_id = models.CharField(max_length=100, blank=True, default="")
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default="")
    razorpay_signature = models.CharField(max_length=255, blank=True, default="")
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        indexes = [models.Index(fields=["status"]),models.Index(fields=["created_at"]),]

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username}"

    @property
    def is_delivered(self):
        return self.status == self.Status.DELIVERED

    @property
    def is_cancelled(self):
        return self.status == self.Status.CANCELLED


class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
    food_item = models.ForeignKey(FoodItem,on_delete=models.PROTECT,related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10,decimal_places=2,help_text="Price of the item at the time of ordering.")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.food_item.name} × {self.quantity}"

class Payment(models.Model):
    class Gateway(models.TextChoices):
        RAZORPAY = "razorpay", "Razorpay"
        DEMO = "demo", "Demo"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    gateway = models.CharField(max_length=20, choices=Gateway.choices, default=Gateway.RAZORPAY)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    gateway_order_id = models.CharField(max_length=100, blank=True, default="")
    gateway_payment_id = models.CharField(max_length=100, blank=True, default="")
    gateway_signature = models.CharField(max_length=255, blank=True, default="")
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["gateway_payment_id"]),
            models.Index(fields=["created_at"]),
        ]

    def mark_paid(self, payment_id, signature):
        self.gateway_payment_id = payment_id
        self.gateway_signature = signature
        self.status = self.Status.PAID
        self.paid_at = timezone.now()

    def mark_failed(self):
        self.status = self.Status.FAILED

    def __str__(self):
        return f"Payment for Order #{self.order_id} - {self.get_status_display()}"
