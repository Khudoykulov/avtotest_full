from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile

class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(required=False, help_text='Ixtiyoriy')
    first_name = forms.CharField(max_length=30, required=False, help_text='Ixtiyoriy')
    last_name = forms.CharField(max_length=30, required=False, help_text='Ixtiyoriy')
    phone_number = forms.CharField(max_length=15, required=False, help_text='Ixtiyoriy')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Customize help texts in Uzbek
        self.fields['username'].help_text = 'Faqat harflar, raqamlar va @/./+/-/_ belgilaridan foydalaning.'
        self.fields['password1'].help_text = 'Parolingiz kamida 8 ta belgidan iborat bo\'lishi kerak.'
        self.fields['password2'].help_text = 'Tasdiqlash uchun bir xil parolni kiriting.'

class UserProfileForm(forms.ModelForm):
    """User profile update form"""
    class Meta:
        model = UserProfile
        fields = ('avatar', 'preferred_language')
        widgets = {
            'preferred_language': forms.Select(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class UserUpdateForm(forms.ModelForm):
    """User information update form"""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
