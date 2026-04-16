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

# Models
from .models import (
    Artwork, Artist, Category, Address, 
    Order, Cart, CartItem, OrderDetail, Payment, Like, Review, Notification
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
    context = {
        'total_users': User.objects.filter(is_staff=False).count(),
        'total_orders': Order.objects.exclude(status='Pending').count(),
        'total_revenue': Order.objects.exclude(status='Cancelled').aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'recent_orders': Order.objects.all().order_by('-order_id')[:5],
        'recent_users': User.objects.filter(is_staff=False).order_by('-date_joined')[:3]
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
    sort_by = request.GET.get('sort', '-prod_id')
    search_query = request.GET.get('q', '')
    selected_cats = request.GET.getlist('cat')
    
    products = Artwork.objects.all()
    if search_query: products = products.filter(Q(title__icontains=search_query))
    if selected_cats: products = products.filter(category_id__in=selected_cats)
    
    sort_mapping = {'title': 'title', '-title': '-title', 'price': 'price', '-price': '-price', 'stock': 'stock_qty', '-stock': '-stock_qty'}
    products = products.order_by(sort_mapping.get(sort_by, '-prod_id'))

    if request.method == 'POST':
        if 'add_category' in request.POST:
            name = request.POST.get('category_name')
            desc = request.POST.get('category_desc')
            if name:
                Category.objects.create(category_name=name, category_desc=desc)
        
        elif 'add_product' in request.POST:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid(): form.save()
        elif 'update_product' in request.POST:
            prod = get_object_or_404(Artwork, prod_id=request.POST.get('prod_id'))
            prod.title = request.POST.get('title'); prod.price = request.POST.get('price')
            prod.stock_qty = request.POST.get('stock_qty'); prod.category_id = request.POST.get('category')
            prod.artist_id = request.POST.get('artist'); prod.description = request.POST.get('description')
            if request.FILES.get('image'): prod.image = request.FILES.get('image')
            prod.save()
        elif 'delete_product' in request.POST:
            get_object_or_404(Artwork, prod_id=request.POST.get('prod_id')).delete()
        return redirect('admin_products')

    return render(request, 'admin/admin_products.html', {
        'products': products, 'categories': Category.objects.all(), 'artists': Artist.objects.all(),
        'p_form': ProductForm(), 'current_sort': sort_by, 'search_query': search_query, 'selected_cats': selected_cats
    })

@user_passes_test(lambda u: u.is_staff, login_url='admin_login')
def admin_orders(request):
    # Fetch orders and "pre-fetch" the users and their addresses to avoid empty fields
    orders = Order.objects.all().order_by('-order_id').select_related('user')
    
    for o in orders:
        o.items = OrderDetail.objects.filter(order=o)
        # Attach the user's default address to the order object for the modal
        o.customer_address = Address.objects.filter(user=o.user, address_type='Default').first()

    if request.method == 'POST' and 'update_status' in request.POST:
        order = get_object_or_404(Order, order_id=request.POST.get('order_id'))
        order.status = request.POST.get('status')
        order.save()
        return redirect('admin_orders')
        
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
    
    # 2. Check if a specific artist is selected
    active_artist_id = request.GET.get('artist_id')
    active_artist = None
    messages_list = []
    
    if active_artist_id:
        active_artist = get_object_or_404(Artist, artist_id=active_artist_id)
        # Fetch the chat history for this artist
        # Replace 'Notification' with your actual model name
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
        'messages_list': messages_list
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
    if request.user.is_authenticated and request.user.is_staff: return redirect('admin_dashboard')
    return render(request, 'products/product_detail.html', {'product': get_object_or_404(Artwork, prod_id=prod_id)})

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
    address = Address.objects.filter(user=request.user, address_type='Default').first()
    
    # Check if this user has been promoted to an Artist
    artist_obj = Artist.objects.filter(user=request.user).first()
    is_artist = artist_obj is not None

    # Status map for the Purchases tabs (Mapping UI names to DB strings)
    status_map = {
        'to_pay': 'To Pay',
        'to_ship': 'Processing',
        'to_receive': 'Shipped',
        'completed': 'Delivered',
        'cancelled': 'Cancelled'
    }

    # 2. HANDLE FORM SUBMISSIONS (POST)
    if request.method == 'POST':
        
        # --- ACTION A: UPDATE PERSONAL INFO & PHOTO ---
        if 'update_personal_info' in request.POST:
            request.user.first_name = request.POST.get('fname')
            request.user.last_name = request.POST.get('lname')
            request.user.save()

            addr, created = Address.objects.get_or_create(user=request.user, address_type='Default')
            if request.FILES.get('profile_pix'):
                addr.profile_pix = request.FILES.get('profile_pix')
            addr.save()
            return redirect('/profile/?tab=account')

        # --- ACTION B: UPDATE ADDRESS MODAL ---
        elif 'update_address' in request.POST:
            addr, created = Address.objects.get_or_create(user=request.user, address_type='Default')
            addr.street = request.POST.get('st_name')
            addr.brgy = request.POST.get('brgy')
            addr.municipality = request.POST.get('municipality')
            addr.zipcode = request.POST.get('zipcode')
            addr.phone_num = request.POST.get('phone')
            addr.latitude = request.POST.get('lat')
            addr.longitude = request.POST.get('lng')
            
            addr.delivery_fname = request.user.first_name
            addr.delivery_lname = request.user.last_name
            addr.save()
            return redirect('/profile/?tab=account')

        # --- ACTION C: ARTIST MESSAGE REPLY ---
        elif 'artist_update_status' in request.POST:
            notif_id = request.POST.get('notif_id')
            new_status = request.POST.get('status_val') 
            
            orig_notif = get_object_or_404(Notification, id=notif_id, artist=artist_obj)
            
            # Create a reply Notification for the Admin
            Notification.objects.create(
                order=orig_notif.order,
                artist=artist_obj,
                message_text=f"ARTIST UPDATE: Status changed to {new_status}.",
                sender_role='Artist',
                status_update=new_status
            )

            # AUTO-UPDATE MAIN ORDER STATUS:
            # If artist says 'Item Picked Up', the order is now officially 'Shipped'
            if new_status == 'Item Picked Up':
                order = orig_notif.order
                order.status = 'Shipped'
                order.save()

            # REMOVED: messages.success calls that were spamming your login page
            return redirect('/profile/?tab=messages')

    # 3. FETCH PURCHASES DATA
    orders_query = Order.objects.filter(user=request.user)
    if status_tab != 'all':
        # Default to 'Processing' if status is missing
        search_status = status_map.get(status_tab, 'Processing')
        orders_query = orders_query.filter(status=search_status)
    
    orders = orders_query.order_by('-order_id')
    for o in orders:
        o.items = OrderDetail.objects.filter(order=o).select_related('product')

    # 4. FETCH ARTIST MESSAGES
    artist_messages = []
    if is_artist:
        artist_messages = Notification.objects.filter(artist=artist_obj).order_by('-timestamp')

    # 5. RENDER
    return render(request, 'products/profile.html', {
        'address': address,
        'orders': orders,
        'active_tab': active_tab,
        'status_tab': status_tab,
        'is_artist': is_artist,
        'artist_messages': artist_messages
    })

# --- 4. SHOPPING BAG & CHECKOUT ---

@login_required
def add_to_cart(request, product_id):
    if request.user.is_staff: return redirect('admin_dashboard')
    if request.method == 'POST':
        product = get_object_or_404(Artwork, prod_id=product_id)
        qty = int(request.POST.get('quantity', 1))
        is_buy_now = request.POST.get('buy_now_mode') == 'true'
        try:
            with transaction.atomic():
                user_cart, _ = Cart.objects.get_or_create(user=request.user)
                if is_buy_now: CartItem.objects.filter(cart=user_cart).update(is_selected=False)
                item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)
                item.quantity = qty if is_buy_now else item.quantity + qty
                item.is_selected = True; item.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': f'Added {product.title} to bag', 'cart_count': CartItem.objects.filter(cart=user_cart).count()})
            return redirect('checkout' if is_buy_now else 'view_cart')
        except Exception as e: return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
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
    user_cart = get_object_or_404(Cart, user=request.user)
    items = CartItem.objects.filter(cart=user_cart, is_selected=True)
    if not items.exists(): return redirect('view_cart')
    address = Address.objects.filter(user=request.user, address_type='Default').first()
    artist_groups = {}
    for i in items:
        if i.product.artist not in artist_groups: artist_groups[i.product.artist] = {'items': [], 'sub': 0}
        artist_groups[i.product.artist]['items'].append(i)
        artist_groups[i.product.artist]['sub'] += float(i.product.price * i.quantity)
    ship = len(artist_groups) * 60.0
    sub = sum(g['sub'] for g in artist_groups.values())
    return render(request, 'products/checkout.html', {'artist_groups': artist_groups, 'total_shipping': ship, 'items_subtotal': sub, 'grand_total': sub + ship, 'address': address})

@login_required
def place_order(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                user_cart = Cart.objects.get(user=request.user)
                items = CartItem.objects.filter(cart=user_cart, is_selected=True)
                if not items.exists(): return redirect('view_cart')
                subtotal = sum(i.product.price * i.quantity for i in items)
                shipping_fee = items.values('product__artist').distinct().count() * 60.0
                pay = Payment.objects.create(method="Cash on Delivery", status="Pending")
                order = Order.objects.create(user=request.user, payment=pay, total_qty=sum(i.quantity for i in items), delivery_fee=shipping_fee, total_amount=float(subtotal) + shipping_fee, status="Processing")
                for i in items:
                    OrderDetail.objects.create(order=order, product=i.product, price=i.product.price, quantity=i.quantity, subtotal=i.product.price * i.quantity)
                    if i.product.stock_qty: i.product.stock_qty -= i.quantity; i.product.save()
                items.delete(); return render(request, 'products/order_success.html', {'order': order})
        except Exception as e: print(f"Order Error: {e}")
    return redirect('catalog')

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    if order.status in ['Processing', 'To Pay', 'Pending']:
        with transaction.atomic():
            for d in OrderDetail.objects.filter(order=order):
                if d.product.stock_qty is not None: d.product.stock_qty += d.quantity; d.product.save()
            order.status = 'Cancelled'; order.save()
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
    # SECURITY: Staff check
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    artist = get_object_or_404(Artist, artist_id=artist_id)
    # Fetch all artworks by this artist
    artworks = Artwork.objects.filter(artist=artist)
    
    # Get the artist's profile picture from their linked user account
    address = None
    if artist.user:
        address = Address.objects.filter(user=artist.user, address_type='Default').first()

    return render(request, 'products/artist_detail.html', {
        'artist': artist,
        'artworks': artworks,
        'address': address
    })