from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import transaction
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
import json
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.http import JsonResponse

# Consolidated Imports from .models
from .models import Artwork, Artist, Category, Stock, CustomUser, CustomerProfile, AdminProfile, Timeline, Order, CartItem, Profile, Payment, AuditLog
# Consolidated Imports from .forms
from .forms import ProductForm, CategoryForm, BicolikhaSignupForm

# --- 1. ADMINISTRATIVE / MANAGEMENT VIEWS ---
# Templates located in 'templates/admin/'

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # 1. Top 3 Stats (Theme: Text Brown)
    total_users = User.objects.count()
    total_orders = Order.objects.exclude(order_status='Pending').count()
    total_revenue = Order.objects.exclude(order_status='Pending').aggregate(Sum('order_total_amount'))['order_total_amount__sum'] or 0

    # 2. User Growth (Last 7 Days)
    today = timezone.now().date()
    growth_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = User.objects.filter(date_joined__date=day).count()
        growth_data.append({'day': day.strftime('%a'), 'count': count})

    # 3. Order Status Distribution (For Doughnut)
    status_counts = list(Order.objects.exclude(order_status='Pending').values('order_status').annotate(count=Count('order_id')))

    # 4. Recent Activity (Combining recent users and orders)
    recent_users = User.objects.all().order_by('-date_joined')[:3]
    
    # 5. Sales by Location (Municipality > Barangay)
    # This groups your real orders by the customer's specific Bicol location
    loc_raw = Order.objects.exclude(order_status='Pending').values(
        'customer__cust_municipality', 
        'customer__cust_brngy'  # Added the 'n' here
    ).annotate(count=Count('order_id'))
    
    location_data = [
        {
            'mun': item['customer__cust_municipality'],
            'brgy': item['customer__cust_brngy'], # Added the 'n' here
            'v': item['count']
        } for item in loc_raw
    ]

    context = {
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'growth_data': growth_data,
        'status_counts': status_counts,
        'recent_orders': Order.objects.exclude(order_status='Pending').order_by('-order_id')[:5],
        'recent_users': User.objects.all().order_by('-date_joined')[:3],
        'location_data': location_data,
    }

    return render(request, 'admin/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def admin_analytics(request):
    # --- Business Data ---
    total_revenue = Order.objects.exclude(order_status='Pending').aggregate(Sum('order_total_amount'))['order_total_amount__sum'] or 0
    
    # FIX: Wrap the .values() query in list() so it can be serialized to JSON
    category_sales = list(Category.objects.annotate(
        total_sold=Count('artwork')
    ).values('category_name', 'total_sold'))

    # FIX: Wrap this in list() as well
    status_counts = list(Order.objects.values('order_status').annotate(
        count=Count('order_id')
    ))

    context = {
        'total_revenue': total_revenue,
        'total_users': User.objects.count(),
        'total_orders': Order.objects.exclude(order_status='Pending').count(),
        'category_sales': category_sales,
        'status_counts': status_counts,
    }
    return render(request, 'admin/admin_analytics.html', context)

@user_passes_test(lambda u: u.is_staff)
def admin_users(request):
    return render(request, 'admin/admin_users.html')

# products/views.py

@user_passes_test(lambda u: u.is_staff)
def admin_manage_artists(request):
    artists = Artist.objects.all()
    
    if request.method == 'POST':
        artist_id = request.POST.get('artist_id')
        artist = get_object_or_404(Artist, artist_id=artist_id)

        # --- UPDATED UNPROMOTE LOGIC ---
        if 'unpromote_artist' in request.POST:
            try:
                with transaction.atomic():
                    # 1. Find the user in the custom 'users' table
                    # We look for a match based on the artist_name 
                    # (In a real app, we'd use a user_id, but we match by name for your SQL structure)
                    c_user = CustomUser.objects.filter(
                        user_fname__icontains=artist.artist_name.split()[0]
                    ).first()
                    
                    if c_user:
                        # 2. Revert role to 'C' (Customer)
                        c_user.user_role = 'C'
                        c_user.save()

                    # 3. Security Audit Log (Requirement 6.C)
                    AuditLog.objects.create(
                        user=request.user,
                        action=f"Revoked Artist Privileges: {artist.artist_name}",
                        ip_address=request.META.get('REMOTE_ADDR')
                    )

                    # 4. Delete the record from the 'artist' table
                    artist.delete()

                return redirect('manage_artists')
            except Exception as e:
                print(f"Unpromote Error: {e}")

        # --- EDIT ARTIST LOGIC (Keep existing) ---
        elif 'edit_artist' in request.POST:
            artist.artist_name = request.POST.get('artist_name')
            artist.artist_contact_num = request.POST.get('artist_contact_num')
            artist.artist_description = request.POST.get('artist_description')
            artist.artist_municipality = request.POST.get('artist_municipality')
            artist.artist_brgy = request.POST.get('artist_brgy')
            artist.artist_zipcode = request.POST.get('artist_zipcode')
            artist.save()
            return redirect('manage_artists')

    return render(request, 'admin/manage_artists.html', {'artists': artists})

@user_passes_test(lambda u: u.is_staff)
def admin_manage_accounts(request):
    # Fetch users who are NOT yet artists (Role 'C')
    users = CustomUser.objects.filter(user_role='C')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        
        # --- DELETE USER LOGIC ---
        if 'delete_user' in request.POST:
            # This deletes from Django Auth User, which cascades to your custom 'users' table
            user_to_delete = get_object_or_404(User, id=user_id)
            user_to_delete.delete()
            return redirect('manage_accounts')

        # --- PROMOTE TO ARTIST LOGIC ---
        elif 'promote_to_artist' in request.POST:
            custom_user = get_object_or_404(CustomUser, user_id=user_id)
            
            with transaction.atomic():
                # 1. Create the record in the 'artist' table
                Artist.objects.create(
                    artist_name=f"{custom_user.user_fname} {custom_user.user_lname}",
                    artist_contact_num=request.POST.get('contact'),
                    artist_municipality=request.POST.get('municipality'),
                    artist_brgy=request.POST.get('brgy'),
                    artist_zipcode=request.POST.get('zipcode'),
                    artist_description="New Bicolikha Artist"
                )
                
                # 2. Update their role to 'A' (Admin/Artist) so they move out of the user list
                custom_user.user_role = 'A'
                custom_user.save()
                
            return redirect('manage_accounts')

    return render(request, 'admin/manage_accounts.html', {'users': users})

@user_passes_test(lambda u: u.is_staff)
def admin_manage_admins(request):
    # Fix theme for Admins page
    admins = User.objects.filter(is_staff=True).order_by('-last_login')
    
    return render(request, 'admin/manage_admins.html', {'admins': admins})

@user_passes_test(lambda u: u.is_staff)
def admin_products(request):
    # 1. GET PARAMETERS FOR FILTERING AND SORTING
    search_query = request.GET.get('q', '')
    selected_cats = request.GET.getlist('cat')  # Gets list of IDs from checkboxes
    sort_by = request.GET.get('sort', '-created_at') # Default to newest

    # 2. BASE QUERY
    products = Artwork.objects.all()

    # 3. APPLY SEARCH (By Product Title or Artist Name)
    if search_query:
        products = products.filter(
            Q(title__icontains=search_query) | 
            Q(artist_ref__artist_name__icontains=search_query)
        )

    # 4. APPLY CATEGORY FILTER (Checklist)
    if selected_cats:
        products = products.filter(category_id__in=selected_cats)

    # 5. APPLY DYNAMIC SORTING
    # The sort_by value comes directly from the template links (e.g., 'price' or '-price')
    products = products.order_by(sort_by)

    # 6. DATA FOR FORMS AND UI
    categories = Category.objects.all()
    artists = Artist.objects.all()
    p_form = ProductForm()
    c_form = CategoryForm()

    # 7. POST REQUEST HANDLING (Add, Update, Delete)
    if request.method == 'POST':
        # --- ADD PRODUCT ---
        if 'add_product' in request.POST:
            p_form = ProductForm(request.POST, request.FILES)
            if p_form.is_valid():
                try:
                    with transaction.atomic():
                        # 1. Handle Stock first
                        qty = p_form.cleaned_data.get('stock_qty') or 0
                        new_stock = Stock.objects.create(
                            stock_quantity=qty, 
                            stock_status='In Stock' if qty > 0 else 'Out of Stock'
                        )
                        
                        # 2. Prepare Product
                        product = p_form.save(commit=False)
                        product.stock = new_stock
                        product.user_id = request.user.id
                        
                        # If image is in FILES but not in p_form for some reason
                        if 'image' in request.FILES:
                            product.image = request.FILES['image']
                        
                        product.save()

                        # 3. Log the action
                        AuditLog.objects.create(
                            user=request.user,
                            action=f"Product Added: {product.title}",
                            ip_address=request.META.get('REMOTE_ADDR')
                        )
                    return redirect('admin_products')
                except Exception as e:
                    # Add error handling here so you know if the DB transaction failed
                    print(f"Error saving product: {e}")
            

        # --- UPDATE PRODUCT (Handled via Modal) ---
        elif 'update_product' in request.POST:
            prod_id = request.POST.get('prod_id')
            product = get_object_or_404(Artwork, prod_id=prod_id)
            
            product.title = request.POST.get('title')
            product.price = request.POST.get('price')
            product.description = request.POST.get('description')
            product.category = get_object_or_404(Category, category_id=request.POST.get('category'))
            product.artist_ref = get_object_or_404(Artist, artist_id=request.POST.get('artist_ref'))
            
            # Update associated Stock
            stock = product.stock
            stock.stock_quantity = request.POST.get('stock_qty')
            stock.stock_status = 'In Stock' if int(stock.stock_quantity) > 0 else 'Out of Stock'
            stock.save()
            
            # Handle Image Update only if a new file was selected
            if request.FILES.get('image'):
                product.image = request.FILES.get('image')
            
            product.save()
            return redirect('admin_products')

        # --- DELETE PRODUCT ---
        elif 'delete_product' in request.POST:
            prod_id = request.POST.get('prod_id')
            product = get_object_or_404(Artwork, prod_id=prod_id)
            with transaction.atomic():
                stock = product.stock
                product.delete()
                stock.delete()
            return redirect('admin_products')

    # Prepare context
    context = {
        'products': products,
        'categories': categories,
        'artists': artists,
        'p_form': p_form,
        'c_form': c_form,
        'current_sort': sort_by,
        'search_query': search_query,
        # Convert selected_cats to integers so the template checkbox can stay 'checked'
        'selected_cats': [int(c) for c in selected_cats],
    }
    
    return render(request, 'admin/admin_products.html', context)
# products/views.py

@user_passes_test(lambda u: u.is_staff)
def admin_orders(request):
    # 1. Get all orders except active 'Pending' carts
    # Order by newest first
    orders = Order.objects.exclude(order_status='Pending').order_by('-order_id')
    
    # 2. Attach items to each order for the Modal display
    for order in orders:
        order.items = CartItem.objects.filter(order=order)

    # 3. Handle Status Update
    if request.method == 'POST' and 'update_status' in request.POST:
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order_to_update = get_object_or_404(Order, order_id=order_id)
        
        # Security Audit Log (Requirement 6.C)
        old_status = order_to_update.order_status
        order_to_update.order_status = new_status
        order_to_update.save()
        
        AuditLog.objects.create(
            user=request.user,
            action=f"Changed Order #BK-{order_id} status from {old_status} to {new_status}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        return redirect('admin_orders')

    return render(request, 'admin/admin_orders.html', {'orders': orders})

@user_passes_test(lambda u: u.is_staff)
def admin_messages(request):
    return render(request, 'admin/admin_messages.html')

# products/views.py

@user_passes_test(lambda u: u.is_staff)
def admin_reports(request):
    # 1. Sales Summary
    sales_data = Order.objects.exclude(order_status='Pending').aggregate(
        total_revenue=Sum('order_total_amount'),
        total_items=Sum('order_total_quantity')
    )

    # 2. Best Selling Products (Top 5)
    # We look at op_cart items from completed orders
    top_products = CartItem.objects.exclude(order__order_status='Pending').values(
        'product__title'
    ).annotate(
        total_sold=Sum('op_quantity'),
        total_earned=Sum('op_subtotal_amount')
    ).order_by('-total_sold')[:5]

    # 3. Security Audit Logs (Requirement 6.C)
    # If you haven't populated the audit_logs table, we show recent orders/users as activity
    from .models import AuditLog # Ensure imported
    audit_logs = AuditLog.objects.all().order_by('-timestamp')[:10]

    context = {
        'sales': sales_data,
        'top_products': top_products,
        'audit_logs': audit_logs,
        'report_date': timezone.now(),
    }
    return render(request, 'admin/admin_reports.html', context)


# --- 2. PUBLIC STOREFRONT VIEWS ---
# Templates located in 'templates/products/'

def catalog(request):
    selected_cat_id = request.GET.get('category')
    categories = Category.objects.all()

    if selected_cat_id:
        cat = get_object_or_404(Category, category_id=selected_cat_id)
        artworks = Artwork.objects.filter(category=cat)
        context = {'view_all': True, 'category': cat, 'artworks': artworks, 'categories': categories}
    else:
        category_data = []
        for cat in categories:
            products = Artwork.objects.filter(category=cat)[:4]
            if products.exists():
                category_data.append({'category': cat, 'products': products})
        context = {'view_all': False, 'category_data': category_data, 'categories': categories}
    
    return render(request, 'products/catalog.html', context)

def product_detail(request, prod_id):
    product = get_object_or_404(Artwork, prod_id=prod_id)
    return render(request, 'products/product_detail.html', {'product': product})

def artists(request):
    all_artists = Artist.objects.all()
    return render(request, 'products/artists.html', {'artists': all_artists})

def about(request):
    return render(request, 'products/about.html')

def popular(request):
    # 1. Get artworks and sort them by the total quantity sold (op_quantity)
    # We use .order_by() here to sort from highest to lowest (-total_sold)
    popular_artworks = Artwork.objects.exclude(cartitem__order__order_status='Pending') \
        .annotate(total_sold=Sum('cartitem__op_quantity')) \
        .order_by('-total_sold')[:8] 

    # 2. Fallback: If no items have been sold yet, show the newest artworks
    if not popular_artworks:
        popular_artworks = Artwork.objects.all().order_by('-created_at')[:8]

    return render(request, 'products/popular.html', {'artworks': popular_artworks})

# products/views.py


@login_required
def profile_view(request):
    # 1. Fetch data from custom SQL tables
    custom_user = get_object_or_404(CustomUser, user_id=request.user.id)
    customer, _ = CustomerProfile.objects.get_or_create(user_id=request.user.id)
    
    active_tab = request.GET.get('tab', 'account')

    if request.method == 'POST':
        # --- ACTION 1: Main Page "Save Changes" (Names and Photo Only) ---
        if 'update_personal_info' in request.POST:
            custom_user.user_fname = request.POST.get('fname')
            custom_user.user_lname = request.POST.get('lname')
            if request.FILES.get('profile_pix'):
                custom_user.profile_pix = request.FILES.get('profile_pix')
            custom_user.save()
            return redirect('/profile/?tab=account')

        # --- ACTION 2: Modal "Submit" (Address and Contact Only) ---
        elif 'update_address' in request.POST:
            try:
                with transaction.atomic():
                    # Update names (since they are also in the modal)
                    custom_user.user_fname = request.POST.get('fname')
                    custom_user.user_lname = request.POST.get('lname')
                    custom_user.save()

                    # Update address details
                    customer.cust_contact_num = request.POST.get('phone')
                    customer.cust_st_name = request.POST.get('st_name')
                    customer.cust_brngy = request.POST.get('brgy')
                    customer.cust_municipality = request.POST.get('municipality')
                    customer.cust_zipcode = request.POST.get('zipcode')

                    lat = request.POST.get('lat')
                    lng = request.POST.get('lng')
                    if lat and lng:
                        customer.cust_latitude = lat
                        customer.cust_longitude = lng

                    customer.save()
                return redirect('/profile/?tab=account')
            except Exception as e:
                print(f"Address Update Error: {e}")

    # 3. Restored all Purchase Tab filters
    status_filter = request.GET.get('status', 'all')
    orders_query = Order.objects.filter(customer=customer).exclude(order_status='Pending')

    if status_filter == 'to_pay':
        orders_query = orders_query.filter(order_status='To Pay')
    elif status_filter == 'to_ship':
        orders_query = orders_query.filter(order_status='Processing')
    elif status_filter == 'to_receive':
        orders_query = orders_query.filter(order_status='Shipped')
    elif status_filter == 'completed':
        orders_query = orders_query.filter(order_status='Delivered')
    elif status_filter == 'cancelled':
        orders_query = orders_query.filter(order_status='Cancelled')
    elif status_filter == 'return':
        orders_query = orders_query.filter(order_status='Returned')

    order_history = orders_query.order_by('-order_id')
    for order in order_history:
        order.items = CartItem.objects.filter(order=order)

    return render(request, 'products/profile.html', {
        'custom_user': custom_user,
        'customer': customer,
        'orders': order_history,
        'active_tab': active_tab,
        'status_tab': status_filter
    })


# --- 3. SHOPPING BAG LOGIC (Priority 1) ---

# products/views.py

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        # 1. Fetch the product from MySQL
        product = get_object_or_404(Artwork, prod_id=product_id)
        
        # 2. Get and sanitize quantity from the form (Requirement 7: Secure Coding)
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1: quantity = 1
        except (ValueError, TypeError):
            quantity = 1

        # 3. Detect Mode: Is it 'Add to Cart' or 'Buy Now'?
        is_buy_now = request.POST.get('buy_now_mode') == 'true'

        try:
            # Atomic Transaction: Ensures the whole chain succeeds or rolls back (Integrity 6.C)
            with transaction.atomic():
                
                # STEP A: Sync with custom 'users' table (Fulfills fk_customer_users)
                CustomUser.objects.get_or_create(
                    user_id=request.user.id,
                    defaults={
                        'user_email': request.user.email,
                        'user_fname': request.user.first_name or request.user.username,
                        'user_lname': request.user.last_name or 'Member',
                    }
                )

                # STEP B: Sync with custom 'customer' table (Fulfills fk_order_customer)
                customer_profile, _ = CustomerProfile.objects.get_or_create(
                    user_id=request.user.id
                )

                # STEP C: Get or Create the 'Pending' Order (Active Bag)
                try:
                    active_order = Order.objects.get(customer=customer_profile, order_status='Pending')
                except Order.DoesNotExist:
                    # Create required Timeline first (Fulfills fk_order_timeline)
                    new_timeline = Timeline.objects.create()
                    active_order = Order.objects.create(
                        customer=customer_profile,
                        timeline=new_timeline,
                        order_status='Pending',
                        order_total_amount=0,
                        order_total_quantity=0
                    )

                # STEP D: BUY NOW ISOLATION LOGIC
                # If 'Buy Now' is clicked, we unselect everything else currently in the bag
                # so the Checkout page only shows THIS specific item.
                if is_buy_now:
                    CartItem.objects.filter(order=active_order).update(is_selected=False)

                # STEP E: Add/Update the specific item in 'op_cart'
                cart_item, created = CartItem.objects.get_or_create(
                    order=active_order,
                    product=product,
                    defaults={
                        'op_quantity': quantity,
                        'op_subtotal_amount': product.price * quantity,
                        'is_selected': True
                    }
                )

                if not created:
                    # If Buy Now: Overwrite quantity. If Add to Cart: Increment quantity.
                    if is_buy_now:
                        cart_item.op_quantity = quantity
                    else:
                        cart_item.op_quantity += quantity
                    
                    # Ensure THIS item is selected for checkout
                    cart_item.is_selected = True
                    # Server-side subtotal calculation (Prevents Price Tampering)
                    cart_item.op_subtotal_amount = cart_item.op_quantity * product.price
                    cart_item.save()

                # Get updated count for the header badge
                cart_count = CartItem.objects.filter(order=active_order).count()

            # --- RESPONSE LOGIC ---
            
            # Case 1: AJAX Request (From 'Add to Cart' button)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'cart_count': cart_count,
                    'message': 'Successfully added to your bag!'
                })
            
            # Case 2: Standard POST (From 'Buy Now' button)
            # We redirect straight to the checkout page
            return redirect('checkout')

        except Exception as e:
            # Log the error for debugging
            print(f"CRITICAL DATABASE ERROR: {e}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Internal Server Error'}, status=500)
            return redirect('catalog')

    return redirect('catalog')

@login_required
def toggle_cart_item(request, item_id):
    if request.method == 'POST':
        # 1. Find the specific item in the bag
        cart_item = get_object_or_404(CartItem, id=item_id, order__customer__user_id=request.user.id)
        
        # 2. Flip the status (True -> False or False -> True)
        cart_item.is_selected = not cart_item.is_selected
        cart_item.save()
        
        # 3. Calculate the NEW total of only SELECTED items
        order = cart_item.order
        selected_items = CartItem.objects.filter(order=order, is_selected=True)
        new_total = sum(item.op_subtotal_amount for item in selected_items)
        
        # 4. Save this total to the order so Checkout can see it
        order.order_total_amount = new_total
        order.save()
        
        return JsonResponse({
            'status': 'success', 
            'new_total': float(new_total),
            'is_selected': cart_item.is_selected
        })
    return JsonResponse({'status': 'error'}, status=400)
@login_required
def view_cart(request):
    try:
        profile = CustomerProfile.objects.get(user_id=request.user.id)
        order = Order.objects.get(customer=profile, order_status='Pending')
        
        # 1. Get ALL items to show in the list
        all_items = CartItem.objects.filter(order=order)
        
        # 2. Filter only SELECTED items to calculate the Grand Total
        selected_items = all_items.filter(is_selected=True)
        grand_total = sum(item.op_subtotal_amount for item in selected_items)
        
        # Update the Order total amount in DB for the final checkout
        order.order_total_amount = grand_total
        
        order.save()
        
    except (Order.DoesNotExist, CustomerProfile.DoesNotExist):
        all_items = []
        grand_total = 0

    return render(request, 'products/cart.html', {
        'cart_items': all_items, 
        'grand_total': grand_total
    })


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, order__customer__user_id=request.user.id)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def checkout_view(request):
    try:
        customer = CustomerProfile.objects.get(user_id=request.user.id)
        order = Order.objects.get(customer=customer, order_status='Pending')
        
        # --- THE STRICT FILTER ---
        # This is what prevents unchecked items from showing up
        cart_items = CartItem.objects.filter(order=order, is_selected=True)
        
        if not cart_items.exists():
            return redirect('view_cart')

        # (Rest of your multi-artist grouping logic goes here...)
        # Ensure you use the 'cart_items' variable filtered above
        artist_groups = {}
        for item in cart_items:
            artist = item.product.artist_ref
            if artist not in artist_groups:
                artist_groups[artist] = {'items': [], 'subtotal': 0}
            artist_groups[artist]['items'].append(item)
            artist_groups[artist]['subtotal'] += float(item.op_subtotal_amount)

        total_shipping = len(artist_groups) * 60.00
        items_subtotal = sum(group['subtotal'] for group in artist_groups.values())
        
        return render(request, 'products/checkout.html', {
            'artist_groups': artist_groups,
            'total_shipping': total_shipping,
            'items_subtotal': items_subtotal,
            'grand_total': items_subtotal + total_shipping,
            'customer': customer
        })
    except:
        return redirect('catalog')



from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from .models import Order, CartItem, CustomerProfile, Payment, Stock

@login_required
def place_order(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                customer = CustomerProfile.objects.get(user_id=request.user.id)
                old_order = Order.objects.get(customer=customer, order_status='Pending')
                
                # 1. Separate Selected (Buying) from Unselected (Staying in Bag)
                buying_items = CartItem.objects.filter(order=old_order, is_selected=True)
                staying_items = CartItem.objects.filter(order=old_order, is_selected=False)

                if not buying_items.exists():
                    return redirect('view_cart')

                # 2. Calculate Final Totals for the items being bought
                artist_ids = buying_items.values_list('product__artist_ref', flat=True).distinct()
                shipping_fee = len(artist_ids) * 60.00
                items_total = float(sum(item.op_subtotal_amount for item in buying_items))

                # 3. IF there are items left behind, move them to a NEW Pending Order
                if staying_items.exists():
                    new_bag_timeline = Timeline.objects.create()
                    new_bag_order = Order.objects.create(
                        customer=customer,
                        timeline=new_bag_timeline,
                        order_status='Pending'
                    )
                    staying_items.update(order=new_bag_order, is_selected=True)

                # 4. Finalize the CURRENT Order (The one being checked out)
                old_order.order_delivery_fee = shipping_fee
                old_order.order_total_amount = items_total + shipping_fee
                old_order.order_status = 'Processing'
                old_order.save()

                # 5. Stock Reduction (Availability Control)
                for item in buying_items:
                    stock = item.product.stock
                    stock.stock_quantity -= item.op_quantity
                    if stock.stock_quantity <= 0:
                        stock.stock_quantity = 0
                        stock.stock_status = 'Out of Stock'
                    stock.save()

                # 6. Audit Trail: Create Payment
                Payment.objects.create(
                    order=old_order,
                    payment_method="Cash on Delivery",
                    payment_reference=f"REF-{old_order.order_id}"
                )

            return render(request, 'products/order_success.html', {'order': old_order})

        except Exception as e:
            print(f"Checkout Crash: {e}")
            return redirect('catalog')
            
    return redirect('catalog')

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, customer__user_id=request.user.id)
    if order.order_status in ['Processing', 'To Pay']:
            try:
                with transaction.atomic():
                    # Fulfills Availability Requirement: Return items to stock
                    for item in CartItem.objects.filter(order=order):
                        item.product.stock.stock_quantity += item.op_quantity
                        item.product.stock.save()
                    order.order_status = 'Cancelled'
                    order.save()
            except Exception as e:
                print(f"Cancel Error: {e}")
    return redirect('/profile/?tab=purchases&status=cancelled')


# --- 4. AUTHENTICATION ---

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

def signup(request):
    if request.method == 'POST':
        form = BicolikhaSignupForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Create the Django Auth User (for Login system)
                    user = form.save(commit=False)
                    user.username = form.cleaned_data['email'] 
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                    
                    # 2. Create the mirrored record in your custom 'users' table
                    # This satisfies all your foreign key constraints for orders
                    CustomUser.objects.create(
                        user_id=user.id,
                        user_fname=form.cleaned_data['first_name'],
                        user_lname=form.cleaned_data['last_name'],
                        user_email=form.cleaned_data['email'],
                        user_contact_num=form.cleaned_data['phone_number'],
                        user_role='C'
                    )
                
                login(request, user, backend='products.backends.EmailOrPhoneBackend')
                return redirect('catalog')
            except Exception as e:
                form.add_error(None, "An account with these details already exists.")
    else:
        form = BicolikhaSignupForm()
    return render(request, 'registration/signup.html', {'form': form})


def create_audit_log(user, action, request):
    from .models import AuditLog
    # Helper to get IP address for the audit log (Security Requirement)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    
    AuditLog.objects.create(
        user=user,
        action=action,
        ip_address=ip
    )


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # Get the user's IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    
    # Create the security log
    AuditLog.objects.create(
        user=user,
        action=f"User {user.username} logged into the system.",
        ip_address=ip
    )



@login_required
def update_cart_quantity(request, item_id, action):
    # Security: Ensure the item belongs to the logged-in user's pending order
    cart_item = get_object_or_404(
        CartItem, 
        id=item_id, 
        order__customer__user_id=request.user.id, 
        order__order_status='Pending'
    )
    
    if action == 'increment':
        # Availability Check: Don't allow adding more than what's in stock
        if cart_item.op_quantity < cart_item.product.stock.stock_quantity:
            cart_item.op_quantity += 1
        else:
            # You could add a django message here saying "Max stock reached"
            pass
            
    elif action == 'decrement':
        # Integrity Check: Don't allow quantity less than 1
        if cart_item.op_quantity > 1:
            cart_item.op_quantity -= 1
            
    # Recalculate subtotal on the server (Data Integrity)
    cart_item.op_subtotal_amount = cart_item.op_quantity * cart_item.product.price
    cart_item.save()
    
    return redirect('view_cart')