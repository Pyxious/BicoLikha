from .models import Cart, CartItem, Category
from django.db.models import Sum

def cart_count_context(request):
    """
    Renamed back to cart_count_context to match your settings.py
    """
    context = {
        'all_categories': Category.objects.all(),
        'cart_count': 0
    }

    if request.user.is_authenticated:
        try:
            # Look for the cart belonging to the user
            user_cart = Cart.objects.filter(user=request.user).first()
            if user_cart:
                # Calculate total quantity of items
                count = CartItem.objects.filter(cart=user_cart).aggregate(Sum('quantity'))['quantity__sum']
                context['cart_count'] = count or 0
        except Exception:
            context['cart_count'] = 0

    return context