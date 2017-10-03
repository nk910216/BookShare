from django.conf.urls import url
from django.contrib.auth import views as auth_view

from .views import signup

urlpatterns = [
    url(r'^signup/$', signup, name='account_signup'), # for sign up
    url(r'^login/$', auth_view.LoginView.as_view(template_name='login.html'),
        name='account_login'),
    url(r'^logout/$', auth_view.LogoutView.as_view(), name='account_logout')
]
