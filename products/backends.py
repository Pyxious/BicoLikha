from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Profile
from django.db.models import Q

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 1. Try to find user by Email OR Username
            user = User.objects.filter(Q(email=username) | Q(username=username)).first()
            
            # 2. If not found, try to find user by Phone Number via the Profile model
            if not user:
                profile = Profile.objects.filter(phone_number=username).first()
                if profile:
                    user = profile.user
            
            # 3. Check the password
            if user and user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None