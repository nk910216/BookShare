from django.contrib import admin

from .models import BookItem, Book, ExchangeItem
# Register your models here.
@admin.register(BookItem)
class BookItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'owner']  

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors',]
    filter_horizontal = ('targeted_by', )

@admin.register(ExchangeItem)
class ExchangeItemAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user']
    filter_horizontal = ('from_item', 'to_item')
