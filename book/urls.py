from django.conf.urls import url

from .views import bookitem_delete

urlpatterns = [
    url(r'^(?P<pk>\d+)/bookitem_detele/$', bookitem_delete, name='bookitem_delete'),
]
