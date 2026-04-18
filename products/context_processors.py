from .models import Cart, CartItem, Category
from django.db.models import Sum

def cart_count_context(request):
    # Initialize with the names your base.html expects
    context = {
        'all_categories': Category.objects.all(),
        'global_cart_count': 0  # CHANGED: Match base.html name
    }

    # Only run logic for logged-in Customers (Admins don't have carts)
    if request.user.is_authenticated and not request.user.is_staff:
        try:
            user_cart = Cart.objects.filter(user=request.user).first()
            if user_cart:
                # OPTION 1: Total items (2 stickers + 1 pin = 3)
                count = CartItem.objects.filter(cart=user_cart).aggregate(Sum('quantity'))['quantity__sum']
                
                # OPTION 2: Unique products (2 stickers + 1 pin = 2 rows)
                # count = CartItem.objects.filter(cart=user_cart).count()
                
                context['global_cart_count'] = count or 0
        except Exception:
            context['global_cart_count'] = 0

    return context