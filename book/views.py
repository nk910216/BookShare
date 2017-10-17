from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods

from .models import BookItem, Book, ExchangeItem
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

    if request.method == 'POST':
        form = ExchangeForm(request.POST, user_from=from_user, user_to=to_user)
        if form.is_valid():
            exchange = form.save(commit=False)
            exchange.from_user = from_user
            exchange.to_user = to_user
            exchange.save()
            form.save_m2m()
            print(exchange.from_item.all(), exchange.to_item.all())
    else:
        form = ExchangeForm(user_from=from_user, user_to=to_user)

    return render(request, 'book_exchange_post.html', 
                  {'form': form, 'to_user': to_user})
