from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# book item, simple desciption only.
# Not a model for a unique book.
class BookItem(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=512)
    description = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey(User, related_name='book_item')

    def __str__(self):
        return self.title
