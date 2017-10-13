from django.contrib import admin

from .models import BookItem, Book
# Register your models here.
@admin.register(BookItem)
class BookItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'owner']  

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors',]
    filter_horizontal = ('targeted_by',)    
