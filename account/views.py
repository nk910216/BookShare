from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required

from book.forms import NewBookItemForm

from .forms import SignUpForm, InfoUpdateForm
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

# @login_required
# def mypage(request):
#    return render(request, 'mypage.html')

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

@login_required
def mypage(request):
    user = request.user
    if request.method == 'POST':
        form = InfoUpdateForm(request.POST)
        if form.is_valid():
            info = form.cleaned_data
            user.first_name = info.get('first_name', '')
            user.last_name = info.get('last_name', '')
            user.email = info.get('email', '')
            user.save()
    else:
        form = InfoUpdateForm(initial = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
            })
    return render(request, 'mypage.html', {'form': form,})
    
