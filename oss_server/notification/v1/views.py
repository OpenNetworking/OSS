import httplib

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .forms import TxNotificationForm


class CsrfExemptMixin(object):
    """
    Exempts the view from CSRF requirements.

    This should be the left-most mixin of a view.
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CsrfExemptMixin, self).dispatch(*args, **kwargs)


class TxNotificationView(CsrfExemptMixin, View):
    def post(self, request, *args, **kwargs):
        form = TxNotificationForm(request.POST)
        if form.is_valid():
            confirm_notification = form.save()
            response = {'notification_id', confirm_notification.id}
            return JsonResponse(response)
        else:
            errors = ', '.join(reduce(lambda x, y: x + y, form.errors.values()))
            response = {'error': errors}
            return JsonResponse(response, status=httplib.BAD_REQUEST)
