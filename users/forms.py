from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    bio = forms.CharField(
        max_length=160,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself...'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'bio', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    pass


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'website', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Bio...'}),
        }
