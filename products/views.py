from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import F, Sum

# Models
from .models import (
    Artwork, Artist, Category, Address, 
    Order, Cart, CartItem, OrderDetail, Payment, Like, Review, Notification, Shipment
)

# Forms (Ensure these match your forms.py exactly)
from .forms import (
    ProductForm, CategoryForm, BicolikhaSignupForm,
    CustomerAuthenticationForm, AdminAuthenticationForm
)

# --- 1. AUTHENTICATION & PORTAL SECURITY ---

class UserLoginView(LoginView):
    """PORTAL 1: CUSTOMER LOGIN - Strictly rejects staff via CustomerAuthenticationForm."""
    template_name = 'registration/login.html'
    authentication_form = CustomerAuthenticationForm
    def get_success_url(self):
        return reverse_lazy('catalog')

class HiddenAdminLoginView(LoginView):
    """PORTAL 2: SECRET ADMIN LOGIN - Strictly rejects customers via AdminAuthenticationForm."""
    template_name = 'admin/admin_login.html'
    authentication_form = AdminAuthenticationForm
    def get_success_url(self):
        return reverse_lazy('admin_dashboard')

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

def logout_view(request):
    logout(request)
    return redirect('catalog')

def signup(request):
    """Register regular customers only."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        form = BicolikhaSignupForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.username = form.cleaned_data['email']
                    user.set_password(form.cleaned_data['password'])
                    user.save() # Names are saved here automatically by the form into auth_user

                    # No more delivery names here
                    Address.objects.create(
                        user=user, 
                        phone_num=form.cleaned_data['phone_number'],
                        address_type='Default'
                    )
                    Cart.objects.get_or_create(user=user)


                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('catalog')
            except Exception as e:
                form.add_error(None, f"Signup Error: {e}")
    else:
        form = BicolikhaSignupForm()
    return render(request, 'registration/signup.html', {'form': form})

# --- 2. ADMINISTRATIVE / MANAGEMENT HUB ---

@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def admin_users(request):
    """General Users overview page for the dashboard."""
    context = {
        'total_users': User.objects.filter(is_staff=False).count(),
        'new_users_today': User.objects.filter(date_joined__date=timezone.now().date()).count(),
        'active_users': User.objects.filter(is_active=True, is_staff=False).count(),
    }
    return render(request, 'admin/admin_users.html', context)

@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def admin_dashboard(request):
    # 1. Calculate Stats
    total_users = User.objects.filter(is_staff=False).count()
    total_orders = Order.objects.exclude(status='Cancelled').count()
    total_products = Artwork.objects.count()
    total_revenue = Order.objects.exclude(status='Cancelled').aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # 2. Performance Chart (Status Distribution)
    status_distribution = list(Order.objects.values('status').annotate(count=Count('order_id')))

    context = {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_revenue': total_revenue,
        'status_distribution': status_distribution,
    }
    return render(request, 'admin/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def admin_analytics(request):
    total_revenue = Order.objects.exclude(status='Cancelled').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    category_sales = list(Category.objects.annotate(total_sold=Sum('artwork__orderdetail__quantity')).values('category_name', 'total_sold'))
    status_counts = list(Order.objects.values('status').annotate(count=Count('order_id')))

    context = {
        'total_revenue': total_revenue,
        'total_users': User.objects.count(),
        'total_orders': Order.objects.count(),
        'category_sales': category_sales,
        'status_counts': status_counts,
    }
    return render(request, 'admin/admin_analytics.html', context)

@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def admin_manage_accounts(request):
    if request.method == 'POST':
        # --- DELETE USER ---
        if 'delete_user' in request.POST:
            user_to_delete = get_object_or_404(User, id=request.POST.get('user_id'))
            if not user_to_delete.is_superuser:
                user_to_delete.delete()
            return redirect('manage_accounts')
            
        # --- PROMOTE TO ARTIST ---
        elif 'promote_to_artist' in request.POST:
            # 1. Get the specific user being promoted
            target_user = get_object_or_404(User, id=request.POST.get('user_id'))
            
            # 2. Create the Artist record AND LINK THE USER
            Artist.objects.create(
                user=target_user, # THIS IS THE CRITICAL LINK
                artist_name=request.POST.get('artist_name'),
                artist_phone_num=request.POST.get('contact'),
                artist_municipality=request.POST.get('municipality'),
                artist_brgy=request.POST.get('brgy'),
                artist_zipcode=request.POST.get('zipcode'),
                artist_description="Verified Artist"
            )
            return redirect('manage_accounts')

    users = User.objects.filter(is_staff=False).order_by('-date_joined')
    for u in users:
        u.address_info = Address.objects.filter(user=u, address_type='Default').first()
        
    return render(request, 'admin/manage_accounts.html', {'users': users})

@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def admin_products(request):
    # 1. GET FILTER/SORT PARAMETERS
    sort_by = request.GET.get('sort', '-prod_id')
    search_query = request.GET.get('q', '')
    selected_cats = request.GET.getlist('cat')

    # 2. HANDLE ACTIONS (POST)
    if request.method == 'POST':
        
        # --- ACTION: ADD CATEGORY ---
        if 'add_category' in request.POST:
            name = request.POST.get('category_name')
            desc = request.POST.get('category_desc')
            if name:
                Category.objects.create(category_name=name, category_desc=desc)
        
        # --- ACTION: ADD PRODUCT ---
        elif 'add_product' in request.POST:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
        
        # --- ACTION: UPDATE PRODUCT ---
        elif 'update_product' in request.POST:
            prod_id = request.POST.get('prod_id')
            prod = get_object_or_404(Artwork, prod_id=prod_id)
            prod.title = request.POST.get('title')
            prod.price = request.POST.get('price')
            prod.stock_qty = request.POST.get('stock_qty')
            prod.description = request.POST.get('description')
            prod.category_id = request.POST.get('category')
            prod.artist_id = request.POST.get('artist')
            if request.FILES.get('image'):
                prod.image = request.FILES.get('image')
            prod.save()

        # --- ACTION: DELETE PRODUCT ---
        elif 'delete_product' in request.POST:
            prod_id = request.POST.get('prod_id')
            get_object_or_404(Artwork, prod_id=prod_id).delete()

        return redirect('admin_products')

    # 3. FETCH INVENTORY DATA (With Search, Filter, and Sort)
    products_query = Artwork.objects.all()
    
    if search_query:
        products_query = products_query.filter(Q(title__icontains=search_query))
    
    if selected_cats:
        products_query = products_query.filter(category_id__in=selected_cats)

    sort_mapping = {
        'title': 'title', '-title': '-title',
        'price': 'price', '-price': '-price',
        'stock': 'stock_qty', '-stock': '-stock_qty'
    }
    products = products_query.order_by(sort_mapping.get(sort_by, '-prod_id'))

    # 4. CALCULATE DASHBOARD ANALYTICS (For the Stat Cards)
    total_count = Artwork.objects.count()
    in_stock = Artwork.objects.filter(stock_qty__gt=0).count()
    low_stock = Artwork.objects.filter(stock_qty__lte=5, stock_qty__gt=0).count()
    
    # Total Value = Sum of (Price * Stock Quantity) for every item
    # We use F() expressions to do the math directly in the database
    total_value = Artwork.objects.aggregate(
        val=Sum(F('price') * F('stock_qty'))
    )['val'] or 0

    # 5. FETCH CHART DATA (Category Distribution)
    cat_distribution = list(Category.objects.annotate(
        count=Count('artwork')
    ).values('category_name', 'count'))

    # 6. RENDER
    return render(request, 'admin/admin_products.html', {
        'products': products,
        'categories': Category.objects.all(),
        'artists': Artist.objects.all(),
        'p_form': ProductForm(),
        'current_sort': sort_by,
        'search_query': search_query,
        'selected_cats': selected_cats,
        # Analytics Context
        'total_count': total_count,
        'in_stock': in_stock,
        'low_stock': low_stock,
        'total_value': total_value,
        'cat_distribution': cat_distribution
    })

@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def admin_orders(request):
    orders = Order.objects.all().order_by('-order_id').select_related('user', 'shipment')
    
    if request.method == 'POST' and 'update_status' in request.POST:
        order = get_object_or_404(Order, order_id=request.POST.get('order_id'))
        new_status = request.POST.get('status')
        order.status = new_status

        Notification.objects.create(
            order=order,
            artist=order.items.first().product.artist, # Link to the first artist in the order
            message_text=f"Order Update: Your order status has been changed to {new_status}.",
            sender_role='System'
        )

        # --- SYNC TO SHIPMENT TABLE ---
        if order.shipment:
            if new_status == 'Shipped':
                order.shipment.shipment_status = 'In Transit'
                order.shipment.shipment_date = timezone.now().date() # Sets the date
            if new_status == 'Delivered':
                # Update Shipment
                if order.shipment:
                    order.shipment.shipment_status = 'Arrived'
                    order.shipment.save()
                
                # Update Payment (THE FIX)
                if order.payment:
                    order.payment.status = 'Paid'
                    order.payment.save()
            elif new_status == 'Cancelled':
                order.shipment.shipment_status = 'Cancelled'
            order.shipment.save()

        order.save()
        return redirect('admin_orders')
    
    # Pre-fetch logic for display...
    for o in orders:
        o.items = OrderDetail.objects.filter(order=o).select_related('product')
        o.customer_address = Address.objects.filter(user=o.user, address_type='Default').first()

    return render(request, 'admin/admin_orders.html', {'orders': orders})

@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def admin_reports(request):
    sales = Order.objects.exclude(status='Cancelled').aggregate(total_revenue=Sum('total_amount'), total_items=Sum('total_qty'))
    top_products = OrderDetail.objects.values('product__title').annotate(total_sold=Sum('quantity'), total_earned=Sum('subtotal')).order_by('-total_sold')[:5]
    return render(request, 'admin/admin_reports.html', {'sales': sales, 'top_products': top_products, 'audit_logs': [], 'report_date': timezone.now()})

@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def admin_manage_artists(request):
    if request.method == 'POST':
        artist = get_object_or_404(Artist, artist_id=request.POST.get('artist_id'))
        if 'unpromote_artist' in request.POST: artist.delete()
        elif 'edit_artist' in request.POST:
            artist.artist_name = request.POST.get('artist_name'); artist.save()
        return redirect('manage_artists')
    return render(request, 'admin/manage_artists.html', {'artists': Artist.objects.all()})

@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def admin_manage_admins(request):
    admins = User.objects.filter(is_staff=True).order_by('-last_login')
    return render(request, 'admin/manage_admins.html', {'admins': admins})

@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def admin_messages(request):
    # 1. Get all artists for the sidebar
    artists = Artist.objects.all().order_by('artist_name')
    artist_updates = Notification.objects.filter(sender_role='Artist').order_by('-timestamp')
    artist_updates.filter(is_read=False).update(is_read=True)
    # 2. Check if a specific artist is selected
    active_artist_id = request.GET.get('artist_id')
    active_artist = None
    messages_list = []
    if active_artist_id:
        active_artist = get_object_or_404(Artist, artist_id=active_artist_id)
        messages_list = Notification.objects.filter(artist=active_artist).order_by('timestamp')
        

    # 3. Handle sending a new message manually
    if request.method == 'POST':
        msg_text = request.POST.get('message')
        artist_id = request.POST.get('artist_id')
        if msg_text and artist_id:
            target_artist = get_object_or_404(Artist, artist_id=artist_id)
            Notification.objects.create(
                artist=target_artist,
                message_text=msg_text,
                sender_role='Admin',
                order_id=1 # Dummy or link to a generic context
            )
            return redirect(f'/management/messages/?artist_id={artist_id}')

    return render(request, 'admin/admin_messages.html', {
        'artists': artists,
        'active_artist': active_artist,
        'messages_list': messages_list,
        'artist_updates': artist_updates
    })

# --- 3. PUBLIC STOREFRONT VIEWS ---

def catalog(request):
    if request.user.is_authenticated and request.user.is_staff: return redirect('admin_dashboard')
    cat_id = request.GET.get('category')
    categories = Category.objects.all()
    if cat_id:
        cat = get_object_or_404(Category, category_id=cat_id)
        return render(request, 'products/catalog.html', {'view_all': True, 'category': cat, 'artworks': Artwork.objects.filter(category=cat), 'categories': categories})
    data = [{'category': c, 'products': Artwork.objects.filter(category=c)[:4]} for c in categories if Artwork.objects.filter(category=c).exists()]
    return render(request, 'products/catalog.html', {'view_all': False, 'category_data': data, 'categories': categories})

def product_detail(request, prod_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    
    product = get_object_or_404(Artwork, prod_id=prod_id)
    # Fetch all reviews for this specific product
    reviews = Review.objects.filter(product=product).order_by('-date_created')
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews
    })

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, review_id=review_id, user=request.user)
    if request.method == 'POST':
        review.rating = request.POST.get('rating')
        review.description = request.POST.get('description')
        if request.FILES.get('review_image'):
            review.image = request.FILES.get('review_image')
        review.save()
    return redirect('product_detail', prod_id=review.product.prod_id)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, review_id=review_id, user=request.user)
    prod_id = review.product.prod_id
    review.delete()
    return redirect('product_detail', prod_id=prod_id)

def artists(request):
    if request.user.is_authenticated and request.user.is_staff: return redirect('admin_dashboard')
    return render(request, 'products/artists.html', {'artists': Artist.objects.all()})

def about(request):
    return render(request, 'products/about.html')

def popular(request):
    trending = Artwork.objects.annotate(sold_count=Sum('orderdetail__quantity')).order_by('-sold_count')[:8]
    return render(request, 'products/popular.html', {'artworks': trending})

@login_required
def profile_view(request):
    # SECURITY GATE: Admins should not be in the customer profile
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    # 1. INITIALIZE BASIC DATA
    active_tab = request.GET.get('tab', 'account')
    status_tab = request.GET.get('status', 'all')
    
    # Primary address for Account Info display
    address = Address.objects.filter(user=request.user, is_default=True).first() or \
              Address.objects.filter(user=request.user).first()
    
    # Full list for the Address section
    all_addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-address_id')
    
    # Check if user is a promoted Artist
    artist_obj = Artist.objects.filter(user=request.user).first()
    is_artist = artist_obj is not None

    # Identify products already reviewed by this user
    reviewed_products = list(Review.objects.filter(user=request.user).values_list('product_id', flat=True))

    # Status mapping for UI Tabs
    status_map = {
        'to_pay': 'To Pay',
        'to_ship': 'Processing',
        'to_receive': 'Shipped',
        'completed': 'Delivered',
        'cancelled': 'Cancelled'
    }

    # 2. HANDLE FORM SUBMISSIONS (POST)
    if request.method == 'POST':
        
        # --- DELETE ADDRESS ---
        if 'delete_address' in request.POST:
            addr_id = request.POST.get('address_id')
            addr = get_object_or_404(Address, address_id=addr_id, user=request.user)
            if not addr.is_default:
                addr.delete()
            return redirect('/profile/?tab=account')
        
        # --- UPDATE PERSONAL INFO & PHOTO ---
        elif 'update_personal_info' in request.POST:
            request.user.first_name = request.POST.get('fname')
            request.user.last_name = request.POST.get('lname')
            request.user.save()
            if address:
                if request.FILES.get('profile_pix'):
                    address.profile_pix = request.FILES.get('profile_pix')
                address.save()
            return redirect('/profile/?tab=account')

        # --- ADD NEW ADDRESS ---
        elif 'add_new_address' in request.POST:
            is_first = not Address.objects.filter(user=request.user).exists()
            Address.objects.create(
                user=request.user, street=request.POST.get('st_name'),
                brgy=request.POST.get('brgy'), municipality=request.POST.get('municipality'),
                zipcode=request.POST.get('zipcode'), phone_num=request.POST.get('phone'),
                latitude=request.POST.get('lat'), longitude=request.POST.get('lng'),
                is_default=is_first
            )
            return redirect('/profile/?tab=account')

        # --- EDIT EXISTING ADDRESS ---
        elif 'update_address' in request.POST:
            addr_id = request.POST.get('address_id')
            addr = get_object_or_404(Address, address_id=addr_id, user=request.user)
            addr.street = request.POST.get('st_name')
            addr.brgy = request.POST.get('brgy')
            addr.municipality = request.POST.get('municipality')
            addr.zipcode = request.POST.get('zipcode')
            addr.phone_num = request.POST.get('phone')
            addr.latitude = request.POST.get('lat')
            addr.longitude = request.POST.get('lng')
            addr.save()
            return redirect('/profile/?tab=account')

        # --- ARTIST MESSAGE REPLY (With Duplicate Protection) ---
        elif 'artist_update_status' in request.POST:
            notif_id = request.POST.get('notif_id')
            new_status = request.POST.get('status_val') 
            orig_notif = get_object_or_404(Notification, id=notif_id, artist=artist_obj)

            # Check if this specific update already exists for this order
            already_sent = Notification.objects.filter(
                order=orig_notif.order, 
                artist=artist_obj, 
                status_update=new_status
            ).exists()

            if not already_sent:
                # CREATE ONLY ONE NOTIFICATION (Sender is Artist)
                # This row will be visible to both Admin and Customer
                Notification.objects.create(
                    order=orig_notif.order,
                    artist=artist_obj,
                    message_text=f"The artist has marked Order #BK-{orig_notif.order.order_id} as '{new_status}'.",
                    sender_role='Artist', # Admin sees this in chat
                    status_update=new_status,
                    is_read=False
                )

                # SYNC ORDER/SHIPMENT STATUS
                if new_status == 'Shipped!':
                    order = orig_notif.order
                    order.status = 'Shipped'
                    if order.shipment:
                        order.shipment.shipment_status = 'In Transit'
                        order.shipment.shipment_date = timezone.now().date()
                        order.shipment.save()
                    order.save()

            return redirect('/profile/?tab=messages')

    # 3. FETCH PURCHASES DATA
    orders_query = Order.objects.filter(user=request.user)
    if status_tab != 'all':
        orders_query = orders_query.filter(status=status_map.get(status_tab, 'Processing'))
    
    orders = orders_query.order_by('-order_id')
    for o in orders:
        o.items = OrderDetail.objects.filter(order=o).select_related('product')
        o.is_cancellable = not Notification.objects.filter(order=o, status_update__in=['Items Prepared', 'Ready for Pickup', 'Item Picked Up', 'Waiting for Courier', 'Shipped!']).exists()

    # 4. CUSTOMER NOTIFICATIONS (System Alerts)
    customer_notifications = Notification.objects.filter(
        order__user=request.user
    ).exclude(sender_role='Admin').order_by('-timestamp') # Show everything except Admin's private notes

    if active_tab == 'notifications':
        customer_notifications.filter(is_read=False).update(is_read=True)
    
    unread_count = customer_notifications.filter(is_read=False).count()

    # 5. ARTIST MESSAGES & EARNINGS LOGIC
    artist_messages = []
    unread_artist_count = 0
    if is_artist:
        artist_messages = Notification.objects.filter(artist=artist_obj, sender_role='Admin').order_by('-timestamp')
        if active_tab == 'messages':
            artist_messages.filter(is_read=False).update(is_read=True)
        unread_artist_count = artist_messages.filter(is_read=False).count()

        for msg in artist_messages:
            # Calculate earnings for this artist for this specific order
            artist_items = OrderDetail.objects.filter(order=msg.order, product__artist=artist_obj)
            msg.artist_subtotal = artist_items.aggregate(Sum('subtotal'))['subtotal__sum'] or 0
            
            # Find current status to disable buttons in HTML
            latest_reply = Notification.objects.filter(
                order=msg.order, artist=artist_obj, sender_role='Artist'
            ).order_by('-timestamp').first()
            msg.current_artist_status = latest_reply.status_update if latest_reply else None

    # 6. RENDER
    return render(request, 'products/profile.html', {
        'address': address, 'all_addresses': all_addresses, 'orders': orders,
        'active_tab': active_tab, 'status_tab': status_tab, 'is_artist': is_artist,
        'artist_messages': artist_messages, 'reviewed_products': reviewed_products,
        'customer_notifications': customer_notifications, 'unread_count': unread_count,
        'unread_artist_count': unread_artist_count
    })

# --- 4. SHOPPING BAG & CHECKOUT ---

@login_required
def add_to_cart(request, product_id):
    # 1. SECURITY: Block admins from shopping
    if request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        product = get_object_or_404(Artwork, prod_id=product_id)
        qty = int(request.POST.get('quantity', 1))
        submit_type = request.POST.get('submit_type') # From the button name/value

        # --- OPTION A: BUY NOW (Does NOT touch the database) ---
        if submit_type == 'buy_now':
            # Redirect to checkout with product info in the URL
            return redirect(f'/checkout/?buy_now=true&prod_id={product_id}&qty={qty}')

        # --- OPTION B: ADD TO BAG (Saves to SQL) ---
        try:
            with transaction.atomic():
                user_cart, _ = Cart.objects.get_or_create(user=request.user)
                item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)
                
                if created:
                    item.quantity = qty
                else:
                    item.quantity += qty # Increment if already in bag
                item.save()

            # Handle AJAX for the flying bag animation
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
                total_count = CartItem.objects.filter(cart=user_cart).count()
                return JsonResponse({
                    'status': 'success',
                    'message': f'Added {product.title} to bag!',
                    'cart_count': total_count
                })
            
            messages.success(request, f"Added {product.title} to your bag.")
            return redirect('product_detail', prod_id=product.prod_id)

        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            return redirect('product_detail', prod_id=product.prod_id)
            
    return redirect('catalog')

@login_required
def view_cart(request):
    if request.user.is_staff: return redirect('admin_dashboard')
    user_cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=user_cart)
    total = sum(i.product.price * i.quantity for i in items if i.is_selected)
    return render(request, 'products/cart.html', {'cart_items': items, 'grand_total': total})

@login_required
def toggle_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.is_selected = not item.is_selected; item.save()
    items = CartItem.objects.filter(cart=item.cart, is_selected=True)
    new_total = sum(i.product.price * i.quantity for i in items)
    return JsonResponse({'status': 'success', 'new_total': float(new_total)})

@login_required
def update_cart_quantity(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if action == 'increment' and (item.product.stock_qty is None or item.quantity < item.product.stock_qty): item.quantity += 1
    elif action == 'decrement' and item.quantity > 1: item.quantity -= 1
    item.save(); return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, id=item_id, cart__user=request.user).delete()
    return redirect('view_cart')

@login_required
def checkout_view(request):
    if request.user.is_staff: return redirect('admin_dashboard')

    # 1. IDENTIFY MODE: Buy Now vs Standard Cart
    buy_now_mode = request.GET.get('buy_now') == 'true'
    artist_groups = {}
    
    if buy_now_mode:
        # VIRTUAL ORDER: Build data from URL, don't look at Cart table
        prod_id = request.GET.get('prod_id')
        qty = int(request.GET.get('qty', 1))
        product = get_object_or_404(Artwork, prod_id=prod_id)
        
        # We create a dictionary that mimics the CartItem structure so the template works
        virtual_item = {
            'product': product,
            'quantity': qty,
            'get_subtotal': product.price * qty
        }
        artist_groups[product.artist] = {'items': [virtual_item], 'sub': float(product.price * qty)}
        
        # Context for the final form
        buy_now_data = {'id': prod_id, 'qty': qty}
    else:
        # STANDARD: Fetch selected items from Cart table
        user_cart = get_object_or_404(Cart, user=request.user)
        selected_items = CartItem.objects.filter(cart=user_cart, is_selected=True).select_related('product', 'product__artist')
        
        if not selected_items.exists():
            return redirect('view_cart')

        for i in selected_items:
            if i.product.artist not in artist_groups:
                artist_groups[i.product.artist] = {'items': [], 'sub': 0}
            artist_groups[i.product.artist]['items'].append(i)
            artist_groups[i.product.artist]['sub'] += float(i.product.price * i.quantity)
        
        buy_now_data = None

    # 2. SHARED DATA (Totals & Addresses)
    total_shipping = len(artist_groups) * 60.0
    items_subtotal = sum(g['sub'] for g in artist_groups.values())
    grand_total = items_subtotal + total_shipping

    all_addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-address_id')
    selected_address = all_addresses.filter(is_default=True).first() or all_addresses.first()

    return render(request, 'products/checkout.html', {
        'artist_groups': artist_groups,
        'total_shipping': total_shipping,
        'items_subtotal': items_subtotal,
        'grand_total': grand_total,
        'all_addresses': all_addresses,
        'selected_address': selected_address,
        'is_buy_now': buy_now_mode,
        'buy_now_id': buy_now_data['id'] if buy_now_data else None,
        'buy_now_qty': buy_now_data['qty'] if buy_now_data else None
    })

@login_required
def place_order(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 1. Determine which items are being bought
                buy_now_id = request.POST.get('buy_now_id')
                buy_now_qty = int(request.POST.get('buy_now_qty', 0))
                
                order_items = [] # List of {'prod': Artwork, 'qty': int}

                if buy_now_id:
                    # MODE: Buy Now (Single Item)
                    product = get_object_or_404(Artwork, prod_id=buy_now_id)
                    order_items.append({'prod': product, 'qty': buy_now_qty})
                else:
                    # MODE: Cart Purchase (Multiple Items)
                    user_cart = get_object_or_404(Cart, user=request.user)
                    cart_items = CartItem.objects.filter(cart=user_cart, is_selected=True)
                    if not cart_items.exists(): return redirect('view_cart')
                    
                    for item in cart_items:
                        order_items.append({'prod': item.product, 'qty': item.quantity})
                    
                    # Clear these specific items from the DB cart
                    cart_items.delete()

                # 2. Get Shipping Address
                addr_id = request.POST.get('selected_address_id')
                user_address = get_object_or_404(Address, address_id=addr_id, user=request.user)

                # 3. Create Supporting Records
                new_shipment = Shipment.objects.create(address=user_address, shipment_status='Preparing')
                new_payment = Payment.objects.create(method="Cash on Delivery", status="Pending")

                # 4. Calculate Final Totals
                subtotal = sum(item['prod'].price * item['qty'] for item in order_items)
                unique_artists = len(set(item['prod'].artist for item in order_items))
                shipping_fee = unique_artists * 60.0

                # 5. Save the Master Order
                order = Order.objects.create(
                    user=request.user, payment=new_payment, shipment=new_shipment,
                    total_qty=sum(item['qty'] for item in order_items),
                    delivery_fee=shipping_fee,
                    total_amount=float(subtotal) + shipping_fee,
                    status="Processing"
                )

                # 6. Save Details, Deduct Stock, and Notify Artists
                for item in order_items:
                    OrderDetail.objects.create(
                        order=order, product=item['prod'], price=item['prod'].price,
                        quantity=item['qty'], subtotal=item['prod'].price * item['qty']
                    )
                    # Inventory Management
                    if item['prod'].stock_qty is not None:
                        item['prod'].stock_qty -= item['qty']
                        item['prod'].save()
                    
                    # Auto-Notification
                    Notification.objects.create(
                        order=order, artist=item['prod'].artist,
                        message_text=f"New Order #BK-{order.order_id} for {item['prod'].title}.",
                        sender_role='Admin'
                    )

                return render(request, 'products/order_success.html', {'order': order})

        except Exception as e:
            print(f"CRITICAL ORDER ERROR: {e}")
            
    return redirect('catalog')

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    # SECURITY CHECK: Has any artist started preparing this?
    already_prepared = Notification.objects.filter(
        order=order, 
        status_update__in=['Items Prepared', 'Ready for Pickup', 'Item Picked Up']
    ).exists()

    if already_prepared:
        messages.error(request, "Cancellation Failed: The artist has already started preparing your order.")
        return redirect('/profile/?tab=purchases')

    # Standard cancellation logic
    if order.status in ['Processing', 'To Pay', 'Pending']:
        with transaction.atomic():
            for d in OrderDetail.objects.filter(order=order):
                if d.product.stock_qty is not None:
                    d.product.stock_qty += d.quantity
                    d.product.save()
            order.status = 'Cancelled'
            order.save()
            
    return redirect('/profile/?tab=purchases&status=cancelled')

@user_passes_test(lambda u: u.is_staff)
def notify_artist(request, order_id, artist_id):
    order = get_object_or_404(Order, order_id=order_id)
    artist = get_object_or_404(Artist, artist_id=artist_id)
    
    Notification.objects.create(
        order=order,
        artist=artist,
        message_text=f"New Order #BK-{order.order_id}. Please prepare the items.",
        sender_role='Admin'
    )
    messages.success(request, f"Artist {artist.artist_name} has been notified.")
    return redirect('admin_orders')

@login_required
def artist_reply(request, notif_id, status):
    # This view is for the Artist portal
    notif = get_object_or_404(Notification, id=notif_id)
    
    # Update the notification with the artist's response
    notif.status_update = status
    notif.message_text = f"Artist has marked items as: {status}"
    notif.sender_role = 'Artist'
    notif.save()
    
    # Optionally update the main order status automatically
    if status == 'Ready for Pickup':
        notif.order.status = 'Processing'
        notif.order.save()
        
    return redirect('admin_messages') # Or the Artist's message page

def artist_detail(request, artist_id):
    # 1. Get current artist
    artist = get_object_or_404(Artist, artist_id=artist_id)
    
    # 2. Find Next and Previous Artists (Circular loop)
    # Get all IDs in order
    all_ids = list(Artist.objects.values_list('artist_id', flat=True).order_by('artist_id'))
    curr_index = all_ids.index(artist_id)
    
    prev_id = all_ids[curr_index - 1] if curr_index > 0 else all_ids[-1]
    next_id = all_ids[curr_index + 1] if curr_index < len(all_ids) - 1 else all_ids[0]

    # 3. Get Artworks and Profile Picture
    artworks = Artwork.objects.filter(artist=artist)[:5] # Limit to 5 for the mockup
    address = Address.objects.filter(user=artist.user, address_type='Default').first()

    return render(request, 'products/artist_detail.html', {
        'artist': artist,
        'artworks': artworks,
        'address': address,
        'prev_id': prev_id,
        'next_id': next_id
    })

def category_detail(request, cat_id):
    # 1. Get current category
    category = get_object_or_404(Category, category_id=cat_id)
    
    # 2. Circular Navigation Logic
    # Get all category IDs in order
    all_cat_ids = list(Category.objects.values_list('category_id', flat=True).order_by('category_id'))
    curr_index = all_cat_ids.index(cat_id)
    
    # Logic to loop back to the start/end
    prev_id = all_cat_ids[curr_index - 1] if curr_index > 0 else all_cat_ids[-1]
    next_id = all_cat_ids[curr_index + 1] if curr_index < len(all_cat_ids) - 1 else all_cat_ids[0]

    # 3. Fetch all products for this category
    artworks = Artwork.objects.filter(category=category)

    return render(request, 'products/category_detail.html', {
        'category': category,
        'artworks': artworks,
        'prev_id': prev_id,
        'next_id': next_id
    })

@login_required
def confirm_order_received(request, order_id):
    # Fetch the order belonging to this user
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    if order.status == 'Shipped':
        with transaction.atomic():
            # 1. Update Order Status
            order.status = 'Delivered'
            
            # 2. SYNC TO SHIPMENT TABLE
            if order.shipment:
                order.shipment.shipment_status = 'Arrived'
                order.shipment.save()
            
            # 3. SYNC TO PAYMENT TABLE (THE FIX)
            if order.payment:
                order.payment.status = 'Paid'
                order.payment.save()
            
            order.save()
            
    return redirect('/profile/?tab=purchases&status=completed')

@login_required
def submit_review(request):
    if request.method == 'POST':
        prod_id = request.POST.get('product_id')
        product = get_object_or_404(Artwork, prod_id=prod_id)
        
        Review.objects.create(
            user=request.user,
            product=product,
            rating=request.POST.get('rating'),
            description=request.POST.get('description'),
            image=request.FILES.get('review_image')
        )
        return redirect('/profile/?tab=purchases&status=completed')