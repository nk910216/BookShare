from django.conf.urls import url
from django.contrib.auth import views as auth_view

from .views import signup, mypage, mybooks, mytargetbooks

urlpatterns = [
    url(r'^signup/$', signup, name='account_signup'), # for sign up
    url(r'^login/$', auth_view.LoginView.as_view(template_name='login.html'),
        name='account_login'),
    url(r'^logout/$', auth_view.LogoutView.as_view(), name='account_logout'),
    url(r'^password/$', 
        auth_view.PasswordChangeView.as_view(template_name='password_change.html'),
        name='account_password_change'),
    url(r'^password/done/$', auth_view.PasswordChangeDoneView.as_view(
            template_name='password_change_done.html'), name='password_change_done'),
    # mypage
    url(r'^mypage/$', mypage, name='account_mypage'),
    url(r'^mybooks/$', mybooks, name='account_mybooks'),
    url(r'^mytargetbooks/$', mytargetbooks, name='account_mytargetbooks')
]
