from .models import Register, Cart, CartItem


def cart_count(request):

    if "user_id" not in request.session:
        return {
            "cart_count": 0
        }

    try:
        user = Register.objects.get(
            id=request.session["user_id"]
        )

        cart = Cart.objects.filter(
            user=user,
            is_active=True
        ).first()

        if cart:
            count = CartItem.objects.filter(cart=cart).count()
        else:
            count = 0

    except Register.DoesNotExist:
        count = 0

    return {
        "cart_count": count
    }