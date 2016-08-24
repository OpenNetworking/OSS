from django.conf.urls import url

from .v1.views import TxNotificationView

urlpatterns = [
    url(r'^v1/confirmation/create$', TxNotificationView.as_view()),
]
