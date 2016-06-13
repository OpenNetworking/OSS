from django.conf.urls import url

from .v1.views import TxConfirmNotificationView

urlpatterns = [
    url(r'^v1/confirmation/create$', TxConfirmNotificationView.as_view()),
]
