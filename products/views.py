from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import transaction
from django.contrib.auth.views import LoginView
from django.db.models import Sum

# Consolidated Imports from .models
from .models import Artwork, Artist, Category, Stock, CustomUser, CustomerProfile, AdminProfile, Timeline, Order, CartItem, Profile, Payment
# Consolidated Imports from .forms
from .forms import ProductForm, CategoryForm, BicolikhaSignupForm

# --- 1. ADMINISTRATIVE / MANAGEMENT VIEWS ---
# Templates located in 'templates/admin/'

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    context = {
        'total_products': Artwork.objects.count(),
        'total_artists': Artist.objects.count(),
        'total_users': User.objects.count(),
    }
    return render(request, 'admin/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def admin_analytics(request):
    return render(request, 'admin/admin_analytics.html')

@user_passes_test(lambda u: u.is_staff)
def admin_users(request):
    return render(request, 'admin/admin_users.html')

@user_passes_test(lambda u: u.is_staff)
def admin_manage_artists(request):
    artists = Artist.objects.all()
    return render(request, 'admin/manage_artists.html', {'artists': artists})

@user_passes_test(lambda u: u.is_staff)
def admin_manage_accounts(request):
    users = User.objects.filter(is_staff=False)
    return render(request, 'admin/manage_accounts.html', {'users': users})

@user_passes_test(lambda u: u.is_staff)
def admin_manage_admins(request):
    admins = User.objects.filter(is_staff=True)
    return render(request, 'admin/manage_admins.html', {'admins': admins})

@user_passes_test(lambda u: u.is_staff)
def admin_products(request):
    products = Artwork.objects.all()
    p_form = ProductForm()
    c_form = CategoryForm()

    if request.method == 'POST':
        if 'add_product' in request.POST:
            p_form = ProductForm(request.POST, request.FILES)
            if p_form.is_valid():
                try:
                    with transaction.atomic():
                        # Sync Registry for MySQL Integrity
                        CustomUser.objects.get_or_create(
                            user_id=request.user.id,
                            defaults={'user_email': request.user.email, 'user_fname': request.user.first_name, 'user_lname': request.user.last_name}
                        )
                        AdminProfile.objects.get_or_create(user_id=request.user.id)
                        
                        new_stock = Stock.objects.create(stock_quantity=1, stock_status='In Stock')
                        product = p_form.save(commit=False)
                        product.stock = new_stock
                        product.user_id = request.user.id
                        product.save()
                    return redirect('admin_products')
                except Exception as e:
                    print(f"Database Error: {e}")
        
        elif 'add_category' in request.POST:
            c_form = CategoryForm(request.POST)
            if c_form.is_valid():
                c_form.save()
                return redirect('admin_products')

    return render(request, 'admin/admin_products.html', {
        'products': products, 'p_form': p_form, 'c_form': c_form
    })

@user_passes_test(lambda u: u.is_staff)
def admin_orders(request):
    orders = Order.objects.all()
    return render(request, 'admin/admin_orders.html', {'orders': orders})

@user_passes_test(lambda u: u.is_staff)
def admin_messages(request):
    return render(request, 'admin/admin_messages.html')

@user_passes_test(lambda u: u.is_staff)
def admin_reports(request):
    return render(request, 'admin/admin_reports.html')


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
    return render(request, 'products/popular.html')

@login_required
def profile_view(request):
    try:
        customer = CustomerProfile.objects.get(user_id=request.user.id)
        
        # Get the 'tab' from the URL (e.g., ?tab=to_ship). Default is 'all'
        status_filter = request.GET.get('tab', 'all')
        
        # Base query: get orders for this customer excluding the active 'Pending' bag
        orders_query = Order.objects.filter(customer=customer).exclude(order_status='Pending')

        # Mapping UI tabs to your Database 'order_status' values
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

        order_history = orders_query.order_by('-order_id')

        # Attach items to each order for display
        for order in order_history:
            order.items = CartItem.objects.filter(order=order)
            
    except CustomerProfile.DoesNotExist:
        order_history = []
        status_filter = 'all'

    return render(request, 'products/profile.html', {
        'orders': order_history,
        'active_tab': status_filter
    })


# --- 3. SHOPPING BAG LOGIC (Priority 1) ---

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Artwork, prod_id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        try:
            with transaction.atomic():
                # Step 1: Sync User and Customer Tables (Satisfies fk_order_customer)
                CustomUser.objects.get_or_create(
                    user_id=request.user.id,
                    defaults={'user_email': request.user.email, 'user_fname': request.user.first_name, 'user_lname': request.user.last_name}
                )
                customer_profile, _ = CustomerProfile.objects.get_or_create(user_id=request.user.id)

                # Step 2: Handle Order (Satisfies fk_order_timeline)
                try:
                    active_order = Order.objects.get(customer=customer_profile, order_status='Pending')
                except Order.DoesNotExist:
                    new_timeline = Timeline.objects.create()
                    active_order = Order.objects.create(customer=customer_profile, timeline=new_timeline, order_status='Pending')

                # Step 3: Add to op_cart
                cart_item, created = CartItem.objects.get_or_create(
                    order=active_order, product=product,
                    defaults={'op_quantity': quantity, 'op_subtotal_amount': product.price * quantity}
                )

                if not created:
                    cart_item.op_quantity += quantity
                    cart_item.op_subtotal_amount = cart_item.op_quantity * product.price
                    cart_item.save()

            return redirect('view_cart')
        except Exception as e:
            print(f"Cart Error: {e}")
            return redirect('catalog')
    return redirect('catalog')

@login_required
def view_cart(request):
    try:
        customer = CustomerProfile.objects.get(user_id=request.user.id)
        order = Order.objects.get(customer=customer, order_status='Pending')
        cart_items = CartItem.objects.filter(order=order)
        grand_total = sum(item.op_subtotal_amount for item in cart_items)
        
        # Update order totals
        order.order_total_amount = grand_total
        order.order_total_quantity = sum(item.op_quantity for item in cart_items)
        order.save()
    except (Order.DoesNotExist, CustomerProfile.DoesNotExist):
        cart_items, grand_total = [], 0

    return render(request, 'products/cart.html', {'cart_items': cart_items, 'grand_total': grand_total})

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
        cart_items = CartItem.objects.filter(order=order)

        if not cart_items:
            return redirect('view_cart')

        # --- LOGIC TO GROUP BY ARTIST ---
        artist_groups = {}
        for item in cart_items:
            artist = item.product.artist_ref
            if artist not in artist_groups:
                artist_groups[artist] = {
                    'items': [],
                    'subtotal': 0,
                    'shipping': 60.00, # Fixed fee per artist
                }
            artist_groups[artist]['items'].append(item)
            artist_groups[artist]['subtotal'] += float(item.op_subtotal_amount)

        # Calculate Grand Totals
        total_shipping = len(artist_groups) * 60.00
        items_subtotal = sum(group['subtotal'] for group in artist_groups.values())
        grand_total = items_subtotal + total_shipping

        # Save the new grand total to the order object for integrity
        order.order_total_amount = grand_total
        order.save()

        context = {
            'artist_groups': artist_groups,
            'total_shipping': total_shipping,
            'items_subtotal': items_subtotal,
            'grand_total': grand_total,
            'customer': customer,
        }
        return render(request, 'products/checkout.html', context)
    except (Order.DoesNotExist, CustomerProfile.DoesNotExist):
        return redirect('catalog')

@login_required
def place_order(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                customer = CustomerProfile.objects.get(user_id=request.user.id)
                order = Order.objects.get(customer=customer, order_status='Pending')
                
                # 1. Recalculate total with shipping fee
                shipping_fee = 60.00
                order.order_total_amount = float(order.order_total_amount) + shipping_fee
                
                # 2. Update status to 'To Pay'
                order.order_status = 'To Pay'
                order.save()
                
                # 3. Create Payment Record (This is where it failed before)
                Payment.objects.create(
                    order=order,
                    payment_method=request.POST.get('payment_method', 'Cash on Delivery'),
                    payment_reference=f"BK-{order.order_id}-REF"
                )

                # 4. Redirect to success
                # Make sure the file is in templates/products/order_success.html
                return render(request, 'products/order_success.html', {'order': order})

        except Exception as e:
            print(f"Error placing order: {e}")
            return redirect('catalog')
            
    return redirect('catalog')

@login_required
def place_order(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                customer = CustomerProfile.objects.get(user_id=request.user.id)
                order = Order.objects.get(customer=customer, order_status='Pending')
                
                # 1. Update the final amount including shipping
                shipping_fee = 60.00
                order.order_total_amount = float(order.order_total_amount) + shipping_fee
                
                # 2. LOCK THE ORDER (Change status)
                # This ensures the next 'add_to_cart' creates a NEW Order ID
                order.order_status = 'To Pay' 
                order.save()
                
                # 3. Create a Payment Record for Audit Trail
                Payment.objects.create(
                    order=order,
                    payment_method=request.POST.get('payment_method', 'Cash on Delivery'),
                    payment_reference=f"BK-{order.order_id}-X"
                )

            return render(request, 'products/order_success.html', {'order': order})
        except Exception as e:
            print(f"Error placing order: {e}")
            return redirect('catalog')
            
    return redirect('catalog')

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