from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib import messages

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
        ExchangeItem.status_change_book_delete(book_item)

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
    exchange_list =\
        from_user.exchange_source.order_by('-created_at').filter(to_user=to_user)
    
    user_exchanges = [exchange for exchange in exchange_list\
            if exchange.is_agree() == True\
            or exchange.is_waiting() == True or exchange.is_reject() == True\
            or exchange.is_target_book_delete() == True]
    
    exchange_list = \
        from_user.exchange_target.order_by('created_at').filter(from_user=to_user)
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
            exchange.save()
            form.save_m2m()
            # exchange.status = ExchangeStatus.REQUEST.value
            print(exchange.from_item.all(), exchange.to_item.all())
            exchange_valid = exchange.status_change_book_request(exchange.pk)
            if exchange_valid == False:
                print('Can not add because of some books already not valid')
                form = ExchangeForm(user_from=from_user, user_to=to_user)
                exchange.delete()
            else:
                # exchange.save()
                # form.save_m2m()
                # print(exchange.from_item.all(), exchange.to_item.all())
                return redirect('post_exchange', username=username)
    else:
        form = ExchangeForm(user_from=from_user, user_to=to_user)

    return render(request, 'book_exchange_form.html', 
            {'form': form, 'to_user': to_user, 'can_post': can_post,
             'max_exchange_amount': get_exchange_max_amount(),})

@login_required
@require_http_methods(['POST', 'GET'])
def regret_exchange(request, username, pk):
    from_user = request.user
    to_user = get_object_or_404(User, username=username)
    exchange = get_object_or_404(ExchangeItem, pk=pk)   

    if from_user == to_user:
        return redirect('account_mypage')

    # if the exchange do not match the from/to
    if exchange.from_user != from_user or exchange.to_user != to_user:
        print('can not regret')
        return redirect('post_exchange', username=username)

    # messages
    words = '用 '
    for books in exchange.from_item.all():
        words += (books.title + ' ')
    words += (' 換 ')
    for books in exchange.to_item.all():
        words += (books.title + ' ')

    result = exchange.status_change_exchange_regret(pk)
    if result:
        words += (' 反悔成功!')
        messages.success(request, words)
    else:
        words += (' 反悔失敗~~~')
        messages.error(request, words)

    return redirect('post_exchange', username=username)

@login_required
@require_http_methods(['POST', 'GET'])
def reject_exchange(request, username, pk):
    to_user = request.user
    from_user = get_object_or_404(User, username=username)
    exchange = get_object_or_404(ExchangeItem, pk=pk)

    if from_user == to_user:
        return redirect('account_mypage')

    # if the exchange do not match the from/to
    if exchange.from_user != from_user or exchange.to_user != to_user:
        print('can not reject, the user is not correct')
        return redirect('post_exchange', username=username)

    # messages
    words = '用 '
    for books in exchange.from_item.all():
         words += (books.title + ' ')
    words += (' 換 ')
    for books in exchange.to_item.all():
        words += (books.title + ' ')

    result = exchange.status_change_exchange_reject(pk)
    if result:
        words += (' 已經被您拒絕!')
        messages.success(request, words)
    else:
        words += (' 拒絕失敗~~~')
        messages.error(request, words)
    return redirect('post_exchange', username=username)

@login_required
@require_http_methods(['POST', 'GET'])
def reject_noticed(request, username, pk):
    from_user = request.user
    to_user = get_object_or_404(User, username=username)
    exchange = get_object_or_404(ExchangeItem, pk=pk)

    if from_user == to_user:
        return redirect('account_mypage')

    # if the exchange do not match the from/to
    if exchange.from_user != from_user or exchange.to_user != to_user:
        print('can not confirm rejection, the user is not correct')
        return redirect('post_exchange', username=username)

    # messages
    words = '用 '
    for books in exchange.from_item.all():
        words += (books.title + ' ')
    words += (' 換 ')
    for books in exchange.to_item.all():
        words += (books.title + ' ')

    result = exchange.status_change_reject_noticed(pk)
    if result:
        words += (' 被拒絕的通知已被您確認!')
        messages.success(request, words)
    else:
        words = ('操作失敗，無法確認被拒絕通知')
        messages.error(request, words)
    return redirect('post_exchange', username=username)
