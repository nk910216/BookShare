from django.conf.urls import url
from django.contrib.auth import views as auth_view

from .views import signup

urlpatterns = [
    url(r'^signup/$', signup, name='account_signup'), # for sign up
]
