from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from .models import Artwork, Artist # Ensure these match your models.py

# --- ADMINISTRATIVE / MANAGEMENT VIEWS ---
# Restricted to Staff only for Security Requirement 6.A

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    total_products = Artwork.objects.count()
    total_artists = Artist.objects.count()
    total_users = User.objects.count()
    context = {
        'total_products': total_products,
        'total_artists': total_artists,
        'total_users': total_users,
    }
    return render(request, 'products/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def admin_analytics(request):
    return render(request, 'products/admin_analytics.html')

@user_passes_test(lambda u: u.is_staff)
def admin_users(request):
    # This is the main page with the 3 big buttons
    return render(request, 'products/admin_users.html')

@user_passes_test(lambda u: u.is_staff)
def admin_manage_artists(request):
    # Page to edit or chat with artists
    artists = Artist.objects.all()
    return render(request, 'products/manage_artists.html', {'artists': artists})

@user_passes_test(lambda u: u.is_staff)
def admin_manage_accounts(request):
    # Page to promote users to artists or delete them
    users = User.objects.filter(is_staff=False) # Only show customers
    return render(request, 'products/manage_accounts.html', {'users': users})

@user_passes_test(lambda u: u.is_staff)
def admin_manage_admins(request):
    # Page to see list of admin accounts
    admins = User.objects.filter(is_staff=True)
    return render(request, 'products/manage_admins.html', {'admins': admins})

@user_passes_test(lambda u: u.is_staff)
def admin_products(request):
    return render(request, 'products/admin_products.html')

@user_passes_test(lambda u: u.is_staff)
def admin_orders(request):
    return render(request, 'products/admin_orders.html')

@user_passes_test(lambda u: u.is_staff)
def admin_messages(request):
    return render(request, 'products/admin_messages.html')

@user_passes_test(lambda u: u.is_staff)
def admin_reports(request):
    return render(request, 'products/admin_reports.html')


# --- PUBLIC VIEWS ---

def catalog(request):
    # This pulls all pieces from your MySQL 'product' table
    artworks = Artwork.objects.all() 
    return render(request, 'products/catalog.html', {'artworks': artworks})

def artists(request):
    # This pulls all artists from your MySQL 'artist' table
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
            # Redirect to catalog after successful signup
            return redirect('catalog')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})