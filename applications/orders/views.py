import hashlib
import hmac
from decimal import Decimal

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from applications.restaurants.models import FoodItem
from .forms import CheckoutForm
from .models import Order, OrderItem, Payment


def _cart_total(cart):
    return sum(
        Decimal(str(item["price"])) * item["quantity"]
        for item in cart.values()
    )


@require_POST
def add_to_cart(request, food_id):
    food = get_object_or_404(
        FoodItem.objects.select_related("restaurant", "category"),
        id=food_id,
        is_available=True,
        restaurant__is_open=True,
        category__is_active=True,
    )

    cart = request.session.get("cart", {})
    key = str(food_id)

    if key in cart:
        cart[key]["quantity"] += 1
    else:
        cart[key] = {
            "name": food.name,
            "restaurant": food.restaurant.name,
            "category": food.category.name,
            "price": str(food.price),
            "quantity": 1,
            "image": food.image.url if food.image else "",
            "is_veg": food.is_veg,
        }

    request.session["cart"] = cart
    request.session.modified = True

    messages.success(request, f"{food.name} added to cart.")
    return redirect("cart")


def cart_view(request):
    cart = request.session.get("cart", {})
    total = _cart_total(cart)
    cart_items = _cart_items(cart)

    return render(request, "cart/cart.html", {
        "cart": cart,
        "cart_items": cart_items,
        "item_count": sum(item["quantity"] for item in cart_items),
        "total": total,
    })


@require_POST
def increase_quantity(request, food_id):
    cart = request.session.get("cart", {})
    key = str(food_id)

    if key in cart:
        cart[key]["quantity"] += 1
        request.session["cart"] = cart
        request.session.modified = True

    return redirect("cart")


@require_POST
def decrease_quantity(request, food_id):
    cart = request.session.get("cart", {})
    key = str(food_id)

    if key in cart:
        if cart[key]["quantity"] > 1:
            cart[key]["quantity"] -= 1
        else:
            del cart[key]

        request.session["cart"] = cart
        request.session.modified = True

    return redirect("cart")


@require_POST
def remove_from_cart(request, food_id):
    cart = request.session.get("cart", {})
    key = str(food_id)

    if key in cart:
        del cart[key]
        request.session["cart"] = cart
        request.session.modified = True
        messages.success(request, "Item removed from cart.")

    return redirect("cart")


def create_razorpay_order(amount, order_id, user):
    amount_in_paise = int(Decimal(str(amount)) * 100)
    key_id = getattr(settings, "RAZORPAY_KEY_ID", "").strip()
    key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "").strip()

    if not key_id or not key_secret:
        return {
            "id": "",
            "amount": amount_in_paise,
            "currency": "INR",
            "status": "demo",
            "demo": True,
        }

    payload = {
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": f"order_{order_id}",
        "notes": {
            "order_id": str(order_id),
            "user": user.username,
        },
    }

    try:
        response = requests.post(
            "https://api.razorpay.com/v1/orders",
            auth=(key_id, key_secret),
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {
            "id": "",
            "amount": amount_in_paise,
            "currency": "INR",
            "status": "demo",
            "demo": True,
        }


def verify_razorpay_signature(order, payment_id, signature):
    key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "").strip()
    if not key_secret:
        return True

    generated_signature = hmac.new(
        key_secret.encode("utf-8"),
        f"{order.razorpay_order_id}|{payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(generated_signature, signature)


@login_required
def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    total = _cart_total(cart)
    cart_items = _cart_items(cart)
    form = CheckoutForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    address=form.cleaned_data["address"],
                    phone=form.cleaned_data["phone"],
                    total_price=total,
                )

                for food_id, item in cart.items():
                    food = get_object_or_404(
                        FoodItem,
                        id=food_id,
                        is_available=True,
                        restaurant__is_open=True,
                        category__is_active=True,
                    )

                    OrderItem.objects.create(
                        order=order,
                        food_item=food,
                        quantity=item["quantity"],
                        price=Decimal(str(item["price"])),
                    )

            razorpay_order = create_razorpay_order(total, order.id, request.user)
            order.razorpay_order_id = razorpay_order.get("id", "")
            order.payment_status = Order.PaymentStatus.PENDING
            order.save(update_fields=["razorpay_order_id", "payment_status"])
            Payment.objects.update_or_create(
                order=order,
                defaults={
                    "user": request.user,
                    "amount": total,
                    "currency": razorpay_order.get("currency", "INR"),
                    "gateway": Payment.Gateway.DEMO if razorpay_order.get("demo") else Payment.Gateway.RAZORPAY,
                    "status": Payment.Status.PENDING,
                    "gateway_order_id": order.razorpay_order_id,
                },
            )

            request.session["cart"] = {}
            request.session.modified = True

            if razorpay_order.get("demo"):
                messages.warning(
                    request,
                    "Live Razorpay checkout is not available. You can complete a secure demo payment on the next page."
                )
            else:
                messages.success(request, "Your order is ready. Complete payment to confirm it.")
            return redirect("payment", order_id=order.id)

        messages.error(request, "Please correct the checkout details.")

    return render(request, "cart/checkout.html", {
        "cart": cart,
        "cart_items": cart_items,
        "item_count": sum(item["quantity"] for item in cart_items),
        "selected_restaurant_name": cart_items[0]["restaurant"] if cart_items else "",
        "total": total,
        "form": form,
    })


@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.is_paid:
        messages.info(request, "This order is already paid.")
        return redirect("order_history")

    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id", "").strip()
        signature = request.POST.get("razorpay_signature", "").strip()
        payment_order_id = request.POST.get("razorpay_order_id", "").strip()

        if not payment_id or not signature:
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect("payment", order_id=order.id)

        if payment_order_id and order.razorpay_order_id and payment_order_id != order.razorpay_order_id:
            messages.error(request, "The payment reference does not match this order.")
            return redirect("payment", order_id=order.id)

        if verify_razorpay_signature(order, payment_id, signature) or not getattr(settings, "RAZORPAY_KEY_SECRET", "").strip():
            payment_record, _ = Payment.objects.get_or_create(
                order=order,
                defaults={
                    "user": order.user,
                    "amount": order.total_price,
                    "currency": "INR",
                    "gateway": Payment.Gateway.DEMO if payment_id.startswith("demo_") else Payment.Gateway.RAZORPAY,
                    "gateway_order_id": order.razorpay_order_id,
                },
            )
            payment_record.mark_paid(payment_id, signature)
            payment_record.save(update_fields=["gateway_payment_id", "gateway_signature", "status", "paid_at", "updated_at"])

            order.razorpay_payment_id = payment_id
            order.razorpay_signature = signature
            order.payment_status = Order.PaymentStatus.PAID
            order.is_paid = True
            order.status = Order.Status.PREPARING
            order.save(update_fields=["razorpay_payment_id", "razorpay_signature", "payment_status", "is_paid", "status"])
            messages.success(request, "Payment complete. Your food is on the way!")
            return redirect("order_history")

        order.payment_status = Order.PaymentStatus.FAILED
        order.save(update_fields=["payment_status"])
        payment_record, _ = Payment.objects.get_or_create(
            order=order,
            defaults={
                "user": order.user,
                "amount": order.total_price,
                "currency": "INR",
                "gateway": Payment.Gateway.RAZORPAY,
                "gateway_order_id": order.razorpay_order_id,
            },
        )
        payment_record.gateway_payment_id = payment_id
        payment_record.gateway_signature = signature
        payment_record.mark_failed()
        payment_record.save(update_fields=["gateway_payment_id", "gateway_signature", "status", "updated_at"])
        messages.error(request, "Payment signature could not be verified.")
        return redirect("payment", order_id=order.id)

    razorpay_key_id = getattr(settings, "RAZORPAY_KEY_ID", "").strip()
    razorpay_key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "").strip()
    has_live_payment = bool(razorpay_key_id and razorpay_key_secret and order.razorpay_order_id)

    return render(request, "orders/payment.html", {
        "order": order,
        "amount": int(order.total_price * 100),
        "currency": "INR",
        "razorpay_key_id": razorpay_key_id,
        "razorpay_order_id": order.razorpay_order_id,
        "has_live_payment": has_live_payment,
    })


@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user,
    ).prefetch_related(
        "items__food_item",
    ).order_by("-created_at")

    return render(request, "orders/order_history.html", {
        "orders": orders,
    })


def _cart_items(cart):
    items = []
    for food_id, item in cart.items():
        price = Decimal(str(item["price"]))
        quantity = item["quantity"]
        items.append({
            **item,
            "food_id": food_id,
            "price": price,
            "quantity": quantity,
            "subtotal": price * quantity,
        })
    return items
