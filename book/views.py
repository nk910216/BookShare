from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib import messages
from django.db import transaction
from django.template.loader import render_to_string

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

        # set the invalid first
        is_valid = book_item.check_and_set_invalid(pk)

        if is_valid == False:
            # it is used by some comfirm exchanges.
            pass
        else:
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
            if exchange.is_source_book_confirm_show() == True\
            or exchange.is_waiting() == True or exchange.is_reject() == True\
            or exchange.is_target_book_delete() == True]
    
    exchange_list = \
        from_user.exchange_target.order_by('created_at').filter(from_user=to_user)
    from_other_exchanges = [exchange for exchange in exchange_list\
            if exchange.is_target_book_confirm_show() == True\
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

@login_required
@require_http_methods(['POST', 'GET'])
def target_book_deleted_noticed(request, username, pk):
    from_user = request.user
    to_user = get_object_or_404(User, username=username)
    exchange = get_object_or_404(ExchangeItem, pk=pk)

    if from_user == to_user:
        return redirect('account_mypage')

    # if the exchange do not match the from/to
    if exchange.from_user != from_user or exchange.to_user != to_user:
        print('can not confirm book deletion, the user is not correct')
        return redirect('post_exchange', username=username)

    # messages
    words = '用 '
    for books in exchange.from_item.all():
        words += (books.title + ' ')
    words += (' 換 ')
    for books in exchange.to_item.all():
        words += (books.title + ' ')

    result = exchange.status_change_target_book_deleted_noticed(pk)
    if result:
        words += (' 中有些書被刪除，因此交換取消的通知已被您確認!')
        messages.success(request, words)
    else:
        words = ('操作失敗，無法確認因書籍刪除而取消交換的通知')
        messages.error(request, words)
    return redirect('post_exchange', username=username)

@login_required
@require_http_methods(['POST', 'GET'])
def confirm_exchange(request, username, pk):
    to_user = request.user
    from_user = get_object_or_404(User, username=username)
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

    result = False # return value of the state change from request-->confirm
    # check if we can cofirm, use the is_valid flag
    with transaction.atomic():
        book_item_list = exchange.from_item.all().union(exchange.to_item.all()).select_for_update().all()
        for book_item in book_item_list:
            if book_item.is_valid == False:
                # can not confirm send message and return.
                messages.error(request, '因為有些書已經被其他交換確認，因此您無法確認這個交換，請重新整理取得最新資訊')
                return redirect('post_exchange', username=username)
        # check and change state of the exchange
        result = exchange.status_change_exchange_confirm(pk)

        if result:
            words += (' 的請求已被您確認! 您的相關物品已被鎖定而無法進行其他交換')
        else:
            words = ('操作失敗，無法確認被拒絕通知')
            messages.error(request, words)
            return redirect('post_exchange', username=username)

        # OK, we can confirm, set all book items to invalid first
        for book_item in book_item_list:
            book_item.is_valid = False
            book_item.book = None
            # book_item.owner = None
            book_item.save()

    # Safe to do the CONFIRM stuff.
    # Now we first regret/reject all our other request.
    to_book = exchange.to_item.all()
    for book_item in to_book:
        for book_exchange in book_item.exchange_source.all():
            book_exchange.status_change_exchange_regret(book_exchange.pk)
        for book_exchange in book_item.exchange_target.all():
            book_exchange.status_change_exchange_reject(book_exchange.pk)
    # Now regret/reject all the request on the other side.
    from_book = exchange.from_item.all()
    for book_item in from_book:
        for book_exchange in book_item.exchange_source.all():
            book_exchange.status_change_exchange_regret(book_exchange.pk)
        for book_exchange in book_item.exchange_target.all():
            book_exchange.status_change_exchange_reject(book_exchange.pk)

    messages.success(request, words)
    return redirect('post_exchange', username=username)

@login_required
@require_http_methods(['POST', 'GET'])
def source_confirm_noticed(request, username, is_ok, pk):
    from_user = request.user
    to_user = get_object_or_404(User, username=username)
    exchange = get_object_or_404(ExchangeItem, pk=pk)   

    if is_ok != '0' and is_ok != '1':
        raise Http404
    is_ok = int(is_ok)

    if from_user == to_user:
        return redirect('account_mypage')

    # if the exchange do not match the from/to
    if exchange.from_user != from_user or exchange.to_user != to_user:
        print('can not notic the confirm, the user is not matched')
        return redirect('post_exchange', username=username)

    # messages
    words = '用 '
    for books in exchange.from_item.all():
        words += (books.title + ' ')
    words += (' 換 ')
    for books in exchange.to_item.all():
        words += (books.title + ' ')

    result = exchange.status_change_confirm_source_noticed(pk, is_ok)

    # need to add the books back to user.
    if result and not is_ok:
        for book_item in exchange.from_item.all():
            # New item
            book_item.pk = None
            book_item.is_valid = True
            book_item.save()
            book_item.exchange_source.clear()
            book_item.exchange_target.clear()
            book_item.check_abstract_book()
            book_item.save()

    if result:
        if is_ok:
            words += (' 已被您確認交換完成，感謝您的使用！')
        else:
            words += (' 已被您認定為交換失敗，已經將您的書重新加入您的書櫃！')
        messages.success(request, words)
    else:
        words = ('的交換可能已經被您確認過，請重新整理更新到最新狀態！')
        messages.error(request, words)
    return redirect('post_exchange', username=username)

@login_required
@require_http_methods(['POST', 'GET'])
def target_confirm_noticed(request, username, is_ok, pk):

    to_user = request.user
    from_user = get_object_or_404(User, username=username)
    exchange = get_object_or_404(ExchangeItem, pk=pk)
    
    if is_ok != '0' and is_ok != '1':
        raise Http404
    is_ok = int(is_ok)

    if from_user == to_user:
        return redirect('account_mypage')

    # if the exchange do not match the from/to
    if exchange.from_user != from_user or exchange.to_user != to_user:
        print('can not notic the confirm, the user is not matched')
        return redirect('post_exchange', username=username)

    # messages
    words = '用 '
    for books in exchange.from_item.all():
        words += (books.title + ' ')
    words += (' 換 ')
    for books in exchange.to_item.all():
        words += (books.title + ' ')

    result = exchange.status_change_confirm_target_noticed(pk, is_ok)

    # need to add the books back to user.
    if result and not is_ok:
        for book_item in exchange.to_item.all():
            # New item
            book_item.pk = None
            book_item.is_valid = True
            book_item.save()
            book_item.exchange_source.clear()
            book_item.exchange_target.clear()
            book_item.check_abstract_book()
            book_item.save()

    if result:
        if is_ok:
            words += (' 已被您確認交換完成，感謝您的使用！')
        else:
            words += (' 已被您認定為交換失敗，已經將您的書重新加入您的書櫃！')
        messages.success(request, words)
    else:
        words = ('的交換可能已經被您確認過，請重新整理更新到最新狀態！')
        messages.error(request, words)
    return redirect('post_exchange', username=username)

# function that returns the book number of user<-->user they can exchange.
def get_overlap_books_from_user(main_user, ref_user):
    # check
    if (not isinstance(main_user, User) or not isinstance(ref_user, User)):
        print('Error type for get_overlap_books_from_user', type(main_user), type(ref_user))

    # main user asked for, and ref user has it
    main_ask_for = ref_user.book_items.filter(is_valid=True, book__targeted_by=main_user)
    ref_rest_books = ref_user.book_items.filter(is_valid=True).difference(main_ask_for)

    # ref user asked for, and main user has it
    ref_ask_for = ref_user.target_books.filter(items__owner=main_user)
    ref_ask_for_rest = ref_user.target_books.all().difference(ref_ask_for)

    # cover count = main_ask_for.count + ref_ask_for.count
    cover_count = main_ask_for.count() + ref_ask_for.count()

    # return with dict.
    book_sets = {'main_ask_for': main_ask_for, 'ref_rest_books': ref_rest_books,
                 'ref_ask_for': ref_ask_for, 'ref_ask_for_rest': ref_ask_for_rest,
                 'cover_count': cover_count, 'user': ref_user}

    return book_sets

@login_required
@require_http_methods(['POST', 'GET'])
def target_candidate_request(request, pk):
    main_user = request.user
    target_book = get_object_or_404(Book, pk=pk)
    user_with_target_book = [item.owner for item in target_book.items.all()]
    print(user_with_target_book)
    # duplicated handle
    user_with_target_book = list(set(user_with_target_book))

    available_user_list = []
    for user in user_with_target_book:
        data = get_overlap_books_from_user(main_user, user)
        available_user_list.append(data)

    html_data = render_to_string('book_exchange_list_info.html', {'available_user_list': available_user_list},
                                 request=request)

    return JsonResponse({'html_data': html_data})