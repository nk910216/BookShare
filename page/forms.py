from django import forms

class SearchForm(forms.Form):
    query_text = forms.CharField(label='',
                                 widget=forms.TextInput(attrs = {'class': 'form-control',
                                    'placeholder': '尋找書名/作者/使用者', 'required': 'true',
                                    }))