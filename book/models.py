from enum import Enum

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned 
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=512)
    # items - the items of this abstract book
    targeted_by = models.ManyToManyField(User, related_name='target_books',
                                         blank=True) 

    def __str__(self):
        return '%s by %s' % (self.title, self.authors)
    
    def add_user_with_book(self, user):
        try:
            print(self.title, self.authors)
            b = Book.objects.get(title=self.title, authors__contains=self.authors)
            print('already exist')
            b.targeted_by.add(user)
        except MultipleObjectsReturned:
            b_list = Book.objects.filter(title=self.title, authors__contains=self.authors)
            for b in b_list:
                b.targeted_by.add(user)
            print('multi books')
        except ObjectDoesNotExist:
            self.save()
            self.targeted_by.add(user)
            print('new')
        

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

# exchange
class ExchangeSourceStatus(Enum):
    SOURCE_NO_STATUS=0
    SOURCE_REQUEST=1
    SOURCE_REGRET=2
    SOURCE_CONFIRM=3
    SOURCE_DELETE=4
    # add below, do not change the string/number above

class ExchangeTargetStatus(Enum):
    TARGET_NO_STATUS=0
    TARGET_ACCEPT=1
    TARGET_DECLINE=2
    TARGET_CONFRIM=3
    TARGET_DELETE=4
    # add below, do not change the string/number above

class ExchangeItem(models.Model):
    from_item = models.ManyToManyField(BookItem, related_name='exchange_source')
    from_user = models.ForeignKey(User, related_name='exchange_source', null=True)
    to_item = models.ManyToManyField(BookItem, related_name='exchange_target')
    to_user = models.ForeignKey(User, related_name='exchange_target', null=True)
    from_status =\
        models.IntegerField(default=ExchangeSourceStatus.SOURCE_NO_STATUS.value)
    to_status =\
        models.IntegerField(default=ExchangeTargetStatus.TARGET_NO_STATUS.value)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        from_name = 'Nouser'
        if self.from_user:
            from_name = self.from_user.username
        to_name = 'Nouser'
        if self.to_user:
            to_name = self.to_user.username
        return "from %s to %s" % (from_name, to_name)

    def is_agree(self):
        if self.from_status == ExchangeSourceStatus.SOURCE_REQUEST.value and\
            self.to_status == ExchangeTargetStatus.TARGET_ACCEPT.value:
            return True
        return False

    def is_waiting(self):
        if self.from_status == ExchangeSourceStatus.SOURCE_REQUEST.value and\
            self.to_status == ExchangeTargetStatus.TARGET_NO_STATUS.value:
            return True
        return False

    def is_decline(self):
        if self.from_status == ExchangeSourceStatus.SOURCE_REQUEST.value and\
            self.to_status == ExchangeTargetStatus.TARGET_DECLINE.value:
            return True
        return False

def get_exchange_max_amount():
    max_amount_per_user = 3
    return max_amount_per_user

def can_user_add_exchange(from_user, to_user):
    count = from_user.exchange_source.filter(to_user=to_user).count()
    if count < get_exchange_max_amount():
        return True
    return False
