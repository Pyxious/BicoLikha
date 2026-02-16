from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from .models import Artwork, Category, Artist, Stock, AdminProfile, CustomUser
from .forms import ProductForm, CategoryForm
from django.db import transaction

# --- ADMINISTRATIVE / MANAGEMENT VIEWS ---

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
    # Main page with the 3 big buttons (Artists, Users, Admins)
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
                    with transaction.atomic(): # Starts a safe DB session
                        # 1. Ensure the Logged-in Admin exists in custom 'users' table
                        custom_user, created = CustomUser.objects.get_or_create(
                            user_id=request.user.id,
                            defaults={
                                'user_role': 'A',
                                'user_fname': request.user.first_name or request.user.username,
                                'user_lname': request.user.last_name or 'Staff',
                                'user_email': request.user.email,
                                'user_password_hash': 'PBKDF2_SECURE'
                            }
                        )

                        # 2. Ensure that ID also exists in the 'admin' table
                        admin_record, created = AdminProfile.objects.get_or_create(
                            user_id=custom_user.user_id,
                            defaults={'admin_access': 'Full Access'}
                        )

                        # 3. Create a Stock entry
                        new_stock = Stock.objects.create(stock_quantity=1, stock_status='In Stock')

                        # 4. Prepare the Product
                        product = p_form.save(commit=False)
                        product.stock = new_stock
                        product.user_id = admin_record.user_id # Link to the validated admin
                        
                        # 5. Final Save
                        product.save()
                        
                    return redirect('admin_products')
                except Exception as e:
                    # This will show you exactly what went wrong in your terminal
                    print(f"Database Error: {e}")
                    p_form.add_error(None, f"Internal Error: {e}")

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
    return render(request, 'admin/admin_orders.html')

@user_passes_test(lambda u: u.is_staff)
def admin_messages(request):
    return render(request, 'admin/admin_messages.html')

@user_passes_test(lambda u: u.is_staff)
def admin_reports(request):
    return render(request, 'admin/admin_reports.html')


# --- PUBLIC VIEWS ---

def catalog(request):
    selected_cat_id = request.GET.get('category')
    categories = Category.objects.all()

    if selected_cat_id:
        # 1. VIEW FOR A SINGLE CATEGORY (Show All items in that category)
        selected_category = Category.objects.get(category_id=selected_cat_id)
        artworks = Artwork.objects.filter(category_id=selected_cat_id)
        
        context = {
            'view_all': True,
            'category': selected_category,
            'artworks': artworks,
            'categories': categories, # Still need this for the navbar/filters
        }
    else:
        # 2. OVERVIEW VIEW (The horizontal row format from your screenshot)
        category_data = []
        for cat in categories:
            # Get the first 4 products for each category to show in the row
            products = Artwork.objects.filter(category_id=cat.category_id)[:4]
            if products.exists():
                category_data.append({
                    'category': cat,
                    'products': products
                })
        
        context = {
            'view_all': False,
            'category_data': category_data,
            'categories': categories,
        }

    return render(request, 'products/catalog.html', context)

def artists(request):
    all_artists = Artist.objects.all()
    return render(request, 'products/artists.html', {'artists': all_artists})

def about(request):
    return render(request, 'products/about.html')

def popular(request):
    return render(request, 'products/popular.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('catalog')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})