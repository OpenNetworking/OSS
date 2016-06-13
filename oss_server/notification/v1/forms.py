from django import forms

from ..models import ConfirmNotification


class ConfirmNotificationForm(forms.ModelForm):
    class Meta:
        model = ConfirmNotification
        fields = ['tx_id', 'confirm_count', 'callback_url']
        error_messages = {
            'tx_id': {
                'required': '`tx_id` is required',
                'invalid': '`tx_id` is invalid'
            },
            'confirm_count': {
                'required': '`confirm_count` is required',
                'min_value': '`confirm_count` should be greater than 1'
            },
            'callback_url': {
                'required': '`callback_url` is required',
                'invalid': '`callback_url` is invalid'
            }
        }
