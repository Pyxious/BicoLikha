from django.contrib import admin
from .models import Artwork, Artist, Category, Address, Order, OrderDetail, Cart, CartItem, Payment, PopularAd

admin.site.register(Artwork)
admin.site.register(Artist)
admin.site.register(Category)
admin.site.register(Address) # Added this
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Payment)
admin.site.register(PopularAd)

# DELETE or COMMENT OUT any reference to CustomerProfile here
# admin.site.register(CustomerProfile)
