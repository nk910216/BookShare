from django.conf.urls import url

from .views import (bookitem_delete, 
        targetbook_delete, post_exchange, post_exchange_form, 
        regret_exchange, reject_exchange, reject_noticed,
        target_book_deleted_noticed, confirm_exchange)

urlpatterns = [
    url(r'^(?P<pk>\d+)/bookitem_detele/$', bookitem_delete, name='bookitem_delete'),
    url(r'^(?P<pk>\d+)/targetbook_detele/$', targetbook_delete, name='targetbook_delete'),
    url(r'^(?P<username>.+)/exchange/$', post_exchange, name='post_exchange'),
    url(r'^(?P<username>.+)/exchange/post/$',
        post_exchange_form, name='post_exchange_form'),
    url(r'^(?P<username>.+)/exchange/regret/(?P<pk>\d+)/$', 
        regret_exchange, name='regret_exchange'),
    url(r'^(?P<username>.+)/exchange/regect/(?P<pk>\d+)/$',
        reject_exchange, name='regect_exchange'),
    url(r'^(?P<username>.+)/exchange/regect_noticed/(?P<pk>\d+)/$',
        reject_noticed, name='reject_noticed'),
    url(r'^(?P<username>.+)/exchange/targetbookdelete_noticed/(?P<pk>\d+)/$',
        target_book_deleted_noticed, name='targetbook_delete_noticed'),
    url(r'^(?P<username>.+)/exchange/confirm_exchange/(?P<pk>\d+)/$',
        confirm_exchange, name='confirm_exchange'),
]
