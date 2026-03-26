from django import forms
from django.contrib.auth.models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control border-0 px-4', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control border-0 px-4', 'placeholder': 'Apellido'}),
            'username': forms.TextInput(attrs={'class': 'form-control border-0 px-4', 'placeholder': 'Usuario', 'readonly': 'readonly'}),
        }
