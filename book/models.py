from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=512)
    # items - the items of this abstract book

    def __str__(self):
        return '%s by %s' % (self.title, self.authors)

# book item, simple desciption only.
# Not a model for a unique book.
class BookItem(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=512)
    description = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey(User, related_name='book_items')

    book = models.ForeignKey(Book, related_name='items', blank=True, null=True,
                             on_delete = models.SET_NULL)

    def __str__(self):
        return self.title

    def check_abstract_book(self):
        try:
            b = Book.objects.get(title=self.title, authors__contains=self.authors)
        except:
            b = Book(title=self.title, authors=self.authors)
            b.save()
        b.items.add(self)

    def can_user_delete(self, user):
        if self.owner == user:
            return True
        if user.has_perm('book.delete_bookitem'):
            return True
        return False
        return False
