from collections import defaultdict

from django.shortcuts import render

from book.models import BookItem
from .forms import SearchForm

# Create your views here.
def pagehome(request):
    ITEM_COUNT_PER_USER = 3
    # search form
    search_form = SearchForm()
    # latest book item
    book_items = BookItem.objects.filter(is_valid=True).order_by('-created_at')
    item_list = []
    user_items_count = defaultdict(int)
    for item in book_items:
        username = item.owner.username
        count = user_items_count[username]
        print(item)
        if count < ITEM_COUNT_PER_USER:
            item_list.append(item)
            user_items_count[username] += 1

    return render(request, 'home.html', {'search_form': search_form, 'lastest_book_items': item_list})
