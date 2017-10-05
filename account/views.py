from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required

from book.forms import NewBookItemForm

from .forms import SignUpForm
# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid:
            user = form.save()
            auth_login(request, user)
            return redirect('page_home')
    else: # GET
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

@login_required
def mypage(request):
    return render(request, 'mypage.html')

@login_required
def mybooks(request):
    # form = NewBookItemForm()
    if  request.method == 'POST':
        form = NewBookItemForm(request.POST)
        if form.is_valid():
            book_item = form.save(commit=False)
            book_item.owner = request.user
            book_item.save()
            form = NewBookItemForm()
    else:
        form = NewBookItemForm()

    books = request.user.book_items.all().order_by('-created_at')

    return render(request, 'mybooks.html', {'form': form, 'books': books})
