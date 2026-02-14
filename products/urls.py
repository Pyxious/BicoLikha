from django.urls import path, include
from . import views

urlpatterns = [
    # Main pages
    path('', views.catalog, name='catalog'),
    path('artists/', views.artists, name='artists'),
    path('about/', views.about, name='about'),
    path('popular/', views.popular, name='popular'),
    
    # Management Pages (Ensure names match the sidebar)
    path('management/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('management/analytics/', views.admin_analytics, name='admin_analytics'),
    path('management/users/', views.admin_users, name='admin_users'),
    path('management/users/artists/', views.admin_manage_artists, name='manage_artists'),
    path('management/users/accounts/', views.admin_manage_accounts, name='manage_accounts'),
    path('management/users/admins/', views.admin_manage_admins, name='manage_admins'),

    path('management/products/', views.admin_products, name='admin_products'),
    path('management/orders/', views.admin_orders, name='admin_orders'),
    path('management/messages/', views.admin_messages, name='admin_messages'),
    path('management/reports/', views.admin_reports, name='admin_reports'),

    # Auth
    path('signup/', views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
]