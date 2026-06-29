def cart_item_count(request):
    cart = request.session.get("cart", {})
    return {
        "cart_item_count": sum(item.get("quantity", 0) for item in cart.values())
    }
