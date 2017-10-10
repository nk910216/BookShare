from book.models import BookItem

book_item = BookItem.objects.all()
for item in book_item:

    if item.book is None:
        print('Need to check book item -', item)
        item.check_abstract_book()
    else:
        print(item, 'is connected with', item.book)
