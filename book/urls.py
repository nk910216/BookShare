from django.conf.urls import url

from .views import (bookitem_delete, 
        targetbook_delete, post_exchange, post_exchange_form, regret_exchange,)

urlpatterns = [
    url(r'^(?P<pk>\d+)/bookitem_detele/$', bookitem_delete, name='bookitem_delete'),
    url(r'^(?P<pk>\d+)/targetbook_detele/$', targetbook_delete, name='targetbook_delete'),
    url(r'^(?P<username>.+)/exchange/$', post_exchange, name='post_exchange'),
    url(r'^(?P<username>.+)/exchange/post/$',
        post_exchange_form, name='post_exchange_form'),
    url(r'^(?P<username>.+)/exchange/regret/(?P<pk>\d+)/$', regret_exchange, name='regret_exchange'),
]
