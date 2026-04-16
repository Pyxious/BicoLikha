from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Address

class EmailOrPhoneBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using 
    either their email or their phone number.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            return None

        try:
            # 1. Try to find the user by email (stored in username field)
            # Or by the email field directly
            user = User.objects.filter(Q(username=username) | Q(email=username)).first()

            # 2. If not found by email, try searching by phone number in the Address table
            if not user:
                address_entry = Address.objects.filter(phone_num=username).first()
                if address_entry:
                    user = address_entry.user

            # 3. If we found a user, check the password
            if user and user.check_password(password):
                return user
                
        except Exception as e:
            print(f"Auth Backend Error: {e}")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None