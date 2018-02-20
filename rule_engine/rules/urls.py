from django.conf.urls import url

from .views import (
    Rules,
    Rule,
)

urlpatterns = [
    url(r'^$', Rules.as_view(), name='rules'),
    url(r'^rule/$', Rule.as_view(), name='rule'),
]
