from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, 
                            widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('username', # 'first_name', 'last_name',
                  'email', 'password1', 'password2')

class InfoUpdateForm(forms.Form):
    last_name = forms.CharField(required=False, max_length=30,
                                label='姓氏')
    first_name = forms.CharField(required=False, max_length=30,
                                 label='名字')
    email = forms.EmailField(required=False, label='電子郵件')
