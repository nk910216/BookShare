from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from .models import BookItem, Book, ExchangeItem 
from .models import ExchangeStatus
from .models import can_user_add_exchange, get_exchange_max_amount
from .forms import ExchangeForm
# Create your views here.
@login_required
@require_http_methods(['POST', 'DELETE'])
def bookitem_delete(request, pk):
    try:
        book_item = BookItem.objects.get(pk=pk)
    except BookItem.DoesNotExit:
        raise Http404

    if book_item.can_user_delete(request.user):

        # should set related exchanges
        for exchange in book_item.exchange_source.all():
            # exchange.clear()
            exchange.status = ExchangeStatus.SOURCE_BOOK_DELETE.value
            exchange.save()
        for exchange in book_item.exchange_target.all():
            # exchange.clear()
            exchange.status = ExchangeStatus.TARGET_BOOK_DELETE.value
            exchange.save()
        
        book_item.delete()
        if request.is_ajax():
            return HttpResponse()
        return redirect('account_mybooks')
    return HttpResponseForbidden()

@login_required
@require_http_methods(['POST', 'DELETE'])
def targetbook_delete(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExit:
        raise Http404

    user = request.user
    book_list = user.target_books.filter(pk=pk)
    for book in book_list:
        book.targeted_by.remove(user)
        print('remove book', book)

    if request.is_ajax():
        return HttpResponse()
    return redirect('account_mytargetbooks')

@login_required
def post_exchange(request, username):
    from_user = request.user
    to_user = get_object_or_404(User, username=username)

    if from_user == to_user:
        return redirect('account_mypage')
    
    # decide if the user can add another exchange.
    can_post = False
    if can_user_add_exchange(from_user, to_user):
        can_post = True

    # query set 
    exchange_list = from_user.exchange_source.filter(to_user=to_user)
    user_exchanges = [exchange for exchange in exchange_list\
            if exchange.is_agree() == True\
            or exchange.is_waiting() == True or exchange.is_reject() == True\
            or exchange.is_target_book_delete() == True]
    
    exchange_list = from_user.exchange_target.filter(from_user=to_user)
    from_other_exchanges = [exchange for exchange in exchange_list\
            if exchange.is_agree() == True\
            or exchange.is_waiting() == True or exchange.is_regret() == True\
            or exchange.is_source_book_delete() == True]

    return render(request, 'book_exchange_post.html', 
                  {'to_user': to_user, 'can_post': can_post,
                   'user_exchanges': user_exchanges,
                   'from_other_exchanges': from_other_exchanges,})

@login_required
def post_exchange_form(request, username):
    from_user = request.user
    to_user = get_object_or_404(User, username=username)
    
    if from_user == to_user:
        return redirect('account_mypage')

    # decide if the user can add another exchange.
    can_post = False
    if can_user_add_exchange(from_user, to_user):
        can_post = True

    if request.method == 'POST':
        form = ExchangeForm(request.POST, user_from=from_user, user_to=to_user)
        if form.is_valid():
            exchange = form.save(commit=False)
            exchange.from_user = from_user
            exchange.to_user = to_user
            exchange.status = ExchangeStatus.REQUEST.value
            exchange.save()
            form.save_m2m()
            print(exchange.from_item.all(), exchange.to_item.all())
            return redirect('post_exchange', username=username)
    else:
        form = ExchangeForm(user_from=from_user, user_to=to_user)

    return render(request, 'book_exchange_form.html', 
            {'form': form, 'to_user': to_user, 'can_post': can_post,
             'max_exchange_amount': get_exchange_max_amount(),})
