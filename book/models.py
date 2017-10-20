from enum import Enum

from django.db import models, transaction
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

    is_valid = models.BooleanField(default=True)

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

    @classmethod
    @transaction.atomic
    def check_and_set_invalid(cls, pk):
        book_item = BookItem.objects.select_for_update().get(pk=pk)
        if book_item.is_valid == False:
            return False
        book_item.is_valid = True
        book_item.book = None
        # book_item.owner = None
        book_item.save()
        return True

# exchange
class ExchangeStatus(Enum):
    NO_STATUS=0
    REQUEST=1
    REJECT=2
    REGRET=3
    CONFIRM=4
    CONFIRM_BY_SOURCE=5
    CONFIRM_BY_TARGET=6
    SOURCE_BOOK_DELETE=7
    TARGET_BOOK_DELETE=8
    FINISH_SUCCESS=9
    FINISH_NOT_SUCCESS=10
    # add below, do not change the string/number above

class ExchangeItem(models.Model):
    from_item = models.ManyToManyField(BookItem, related_name='exchange_source')
    from_user = models.ForeignKey(User, related_name='exchange_source', null=True)
    to_item = models.ManyToManyField(BookItem, related_name='exchange_target')
    to_user = models.ForeignKey(User, related_name='exchange_target', null=True)
    status = models.IntegerField(default=ExchangeStatus.NO_STATUS.value)
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
        if self.status == ExchangeStatus.CONFIRM.value or\
            self.status == ExchangeStatus.CONFIRM_BY_SOURCE.value or\
            self.status == ExchangeStatus.CONFIRM_BY_TARGET.value:
            return True
        return False

    def is_confirm(self):
        if self.status == ExchangeStatus.CONFIRM.value:
            return True
        return False

    def is_soruce_double_confirm(self):
        if self.status == ExchangeStatus.CONFIRM_BY_SOURCE.value:
            return True
        return False

    def is_target_double_confirm(self):
        if self.status == ExchangeStatus.CONFIRM_BY_TARGET.value:
            return True
        return False

    def is_waiting(self):
        if self.status == ExchangeStatus.REQUEST.value:
            return True
        return False

    def is_reject(self):
        if self.status == ExchangeStatus.REJECT.value:
            return True
        return False

    def is_regret(self):
        if self.status == ExchangeStatus.REGRET.value:
            return True
        return False

    def is_source_book_delete(self):
        if self.status == ExchangeStatus.SOURCE_BOOK_DELETE.value:    
            return True
        return False

    def is_target_book_delete(self):
        if self.status == ExchangeStatus.TARGET_BOOK_DELETE.value:
            return True
        return False
    
    # Change state of all exchanges when one book item is deleted.
    @classmethod
    @transaction.atomic
    def status_change_book_delete(cls, book_item):
        exchange_list = book_item.exchange_source.select_for_update().all()
        for exchange in exchange_list:
            if exchange.status == ExchangeStatus.CONFIRM.value:
                exchange.from_item.remove(book_item)
                exchange.status = ExchangeStatus.SOURCE_BOOK_DELETE.value
                exchange.save()
            else: # we can remove directly, because it dose not matter to the other user
                exchange.delete()

        exchange_list = book_item.exchange_target.select_for_update().all()
        for exchange in exchange_list:
            if exchange.status == ExchangeStatus.CONFIRM.value or\
                exchange.status == ExchangeStatus.REQUEST.value:
                exchange.to_item.remove(book_item)
                exchange.status = ExchangeStatus.TARGET_BOOK_DELETE.value
                exchange.save()
            else: # we can remove directly, because it dose not matter to the other user
                exchange.delete()

    # Change state for exchange from no_status --> request. 
    #   we should also check the book items related to it.
    @classmethod
    @transaction.atomic
    def status_change_book_request(cls, pk):
        exchange = cls.objects.select_for_update().get(pk=pk)
        from_books = exchange.from_item.select_for_update().all()
        to_books = exchange.to_item.select_for_update().all()
        exchange.status = ExchangeStatus.NO_STATUS.value

        for book in from_books:
            if book.is_valid == False:
                return False
        for book in to_books:
            if book.is_valid == False:
                return False
        exchange.status = ExchangeStatus.REQUEST.value
        exchange.save()
        return True

    # Change status for exchange from request --> rejret
    # return a dict with 'is_valid' and 'message' for more usage
    @classmethod
    @transaction.atomic
    def status_change_exchange_regret(cls, pk):
        exchange = cls.objects.select_for_update().get(pk=pk)
        
        if exchange.status != ExchangeStatus.REQUEST.value:
            return False
        exchange.from_item.clear()
        exchange.to_item.clear()
        exchange.from_user = None
        exchange.to_user = None
        exchange.delete()
        return True

    # Change status for exchange from request --> reject
    @classmethod
    @transaction.atomic
    def status_change_exchange_reject(cls, pk):
        exchange = cls.objects.select_for_update().get(pk=pk)

        if exchange.status != ExchangeStatus.REQUEST.value:
            return False

        exchange.status = ExchangeStatus.REJECT.value
        exchange.save()
        return True

    # Change status for exchange from reject-->FINISH_NOT_SUCCESS
    @classmethod
    @transaction.atomic
    def status_change_reject_noticed(cls, pk):
        exchange = cls.objects.select_for_update().get(pk=pk)

        if exchange.status != ExchangeStatus.REJECT.value:
            return False
        exchange.from_item.clear()
        exchange.to_item.clear()
        exchange.from_user = None
        exchange.to_user = None
        exchange.delete()
        return True

    # Change status for exchange from SOURCE_BOOK_DELETE-->FINISH_NOT_SUCCESS
    @classmethod
    @transaction.atomic
    def status_change_target_book_deleted_noticed(cls, pk):
        exchange = cls.objects.select_for_update().get(pk=pk)

        if exchange.status != ExchangeStatus.TARGET_BOOK_DELETE.value:
            return False
        exchange.from_item.clear()
        exchange.to_item.clear()
        exchange.from_user = None
        exchange.to_user = None
        exchange.delete()
        return True

def get_exchange_max_amount():
    max_amount_per_user = 3
    return max_amount_per_user

def can_user_add_exchange(from_user, to_user):
    count = from_user.exchange_source.filter(to_user=to_user).count()
    if count < get_exchange_max_amount():
        return True
    return False
