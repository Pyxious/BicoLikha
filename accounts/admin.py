from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Contact Info', {'fields': ('phone_number',)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Contact Info', {'fields': ('phone_number',)}),
    )

