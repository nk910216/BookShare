from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .models import BookItem
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
