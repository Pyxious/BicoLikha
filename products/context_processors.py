# products/context_processors.py
from .models import CartItem, Order, CustomerProfile

def cart_count_context(request):
    if request.user.is_authenticated:
        try:
            # Find the active bag for the logged-in user
            customer = CustomerProfile.objects.get(user_id=request.user.id)
            order = Order.objects.get(customer=customer, order_status='Pending')
            # Count items in op_cart
            count = CartItem.objects.filter(order=order).count()
            return {'global_cart_count': count}
        except:
            return {'global_cart_count': 0}
    return {'global_cart_count': 0}