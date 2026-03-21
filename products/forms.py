from django import forms
from django.contrib.auth.models import User
from .models import Artwork, Category, Artist, Profile

# --- CUSTOM SIGNUP FORM (For Customers) ---
class BicolikhaSignupForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'bicol-input'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'bicol-input'}))
    phone_number = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'bicol-input', 'placeholder': '09xxxxxxxxx'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'bicol-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'bicol-input'}))
    
    agree_policy = forms.BooleanField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if Profile.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone

# --- ADMIN FORMS (For Management Hub) ---
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name']
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['title', 'description', 'price', 'category', 'artist_ref', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'artist_ref': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }