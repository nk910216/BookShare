from django import forms

from .models import BookItem, Book, ExchangeItem

class ExchangeForm(forms.ModelForm):
    from_item = forms.ModelMultipleChoiceField(queryset=BookItem.objects.all(),
                widget=forms.CheckboxSelectMultiple())
    to_item = forms.ModelMultipleChoiceField(queryset=BookItem.objects.all(),
                widget=forms.CheckboxSelectMultiple())
    
    def __init__(self, *args, **kwargs):
        user_from = kwargs.pop('user_from')
        user_to = kwargs.pop('user_to')
        super(ExchangeForm, self).__init__(*args, **kwargs)
        
        print('form : ', user_from)
        print('to : ', user_to)
        
        self.fields['from_item'].queryset = user_from.book_items#BookItem.objects.filter(owner=user_from)
        self.fields['to_item'].queryset = user_to.book_items#BookItem.objects.filter(owner=user_to)
        self.fields['from_item'].label = '我想拿來交換的書'
        self.fields['to_item'].label = '我想交換到的書'    
    
    class Meta:
        model = ExchangeItem
        fields = ('from_item', 'to_item',)

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
