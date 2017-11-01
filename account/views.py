from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required

from book.forms import NewBookItemForm, NewTartgetBookForm

from .forms import SignUpForm, InfoUpdateForm
from .models import Profile
# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
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
            # add item's abstract book
            book_item.check_abstract_book()
            
            form = NewBookItemForm()
    else:
        form = NewBookItemForm()

    books = request.user.book_items.filter(is_valid=True).order_by('-created_at')

    return render(request, 'mybooks.html', {'form': form, 'books': books})

@login_required
def mytargetbooks(request):
    if request.method == 'POST':
        form = NewTartgetBookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.add_user_with_book(request.user)
            
            form = NewTartgetBookForm()
    else:
        form = NewTartgetBookForm()
    books = request.user.target_books.all()

    return render(request, 'mytargetbook.html', {'form': form, 'books': books})

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
            user.profile.city = info.get('city', user.profile.city)
            user.profile.exchange_method = info.get('exchange_method', user.profile.exchange_method)
            user.profile.area_description = info.get('area_description', user.profile.area_description)
            user.profile.contact_description = info.get('contact_description', user.profile.contact_description)
            user.save()
    else:
        print(user.profile.area_description)
        form = InfoUpdateForm(initial = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'city': user.profile.city,
                'exchange_method': user.profile.exchange_method,
                'area_description': user.profile.area_description,
                'contact_description': user.profile.contact_description,
            })
    return render(request, 'mypage.html', {'form': form,})
    
