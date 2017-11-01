from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile

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
    exchange_method = forms.ChoiceField(choices = Profile.EXCHANGE_MEOTHOD_COHICES, 
        label='交換方式')
    city = forms.ChoiceField(choices = Profile.CITY_CHOICES, label='面交縣市 (可面交地點的所在縣市)')
    area_description = forms.CharField(label='面交簡短地點 (例如：捷運公館/台中火車站/八五大樓前)', 
        max_length=30, required=False)
    contact_description = forms.CharField(label='聯絡方式 (如果交易成功後對方能看到的聯絡方式)', 
        max_length=500, required=False, widget=forms.Textarea)