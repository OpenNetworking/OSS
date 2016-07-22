from __future__ import unicode_literals

import uuid

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    callback_url = models.URLField()
    creation_time = models.DateTimeField(auto_now_add=True)
    is_notified = models.BooleanField(default=False, editable=False)
    notification_attempts = models.PositiveIntegerField(default=0, editable=False)
    notification_time = models.DateTimeField(blank=True, null=True)


class TxNotification(Notification):
    tx_id = models.CharField(
        max_length=32,
        validators=[RegexValidator(r'^[0-9a-fA-F]{32}$')]
    )
    confirm_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1, 'confirm count should be greater than 1')]
    )
