from django.shortcuts import render

from .forms import SearchForm

# Create your views here.
def pagehome(request):
    search_form = SearchForm()
    return render(request, 'home.html', {'search_form': search_form})
