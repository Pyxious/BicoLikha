from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import CustomUser # Points to your 'users' table
from django.db.models import Q

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 1. Try finding by Email or Username (Django auth_user table)
            user = User.objects.filter(Q(email=username) | Q(username=username)).first()
            
            # 2. If not found, try finding by Phone Number in your custom 'users' table
            if not user:
                custom_user = CustomUser.objects.filter(user_contact_num=username).first()
                if custom_user:
                    user = User.objects.get(id=custom_user.user_id)
            
            # 3. Check password
            if user and user.check_password(password):
                return user
        except Exception:
            return None