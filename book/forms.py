from django import forms

from .models import BookItem, Book

class NewTartgetBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'authors',]

        labels = {
            'title': ('書名'),
            'authors': ('作者'),
        }

        error_messages = {
            'title': {'max_length': ('字數超出限制')},
            'authors': {'max_length': ('字數超出限制')},
        }

class NewBookItemForm(forms.ModelForm):

    class Meta:
        model = BookItem
        fields = ['title', 'authors', 'description',]
        
        labels = {
            'title': ('書名'),
            'authors': ('作者'),
            'description': ('書況簡短描述'),
        }

        help_texts = {
            'description': ('例子：全新無畫線, 書腰不見')        
        }

        error_messages = {
            'title': {'max_length': ('字數超出限制')},
            'authors': {'max_length': ('字數超出限制')},
            'description': {'max_length': ('字數超出限制')},
        }
