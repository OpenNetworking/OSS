from __future__ import unicode_literals
from collections import OrderedDict

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
import uuid
from django.db import connection

from .validators import validate_address


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    callback_url = models.URLField()
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AddressSubscription(Subscription):
    address = models.CharField(
        max_length=34,
        validators=[validate_address]
    )

    def as_dict(self):
        return OrderedDict([
            ('id', self.id),
            ('address', self.address),
            ('callback_url', self.callback_url),
            ('created_time', self.created_time)
        ])


class TxSubscription(Subscription):
    tx_hash = models.CharField(
        max_length=64,
        validators=[RegexValidator(r'^[0-9a-fA-F]{64}$')],
    )
    confirmation_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1, 'confirmation_count should be greater than 1')]
    )

    def get_notify_block_time(self):
        uuid_hex = self.id.hex
        cursor = connection.cursor()
        time = 0
        try:
            cursor.execute("select blocktable.time as 'time' \
                from explorer_block as blocktable, \
                ( \
                    select block.height as height, sub.confirmation_count as confirmation \
                    from notification_txsubscription sub \
                    left join explorer_tx tx on (tx.hash = sub.tx_hash) \
                    left join explorer_block block on (block.id = tx.block_id) \
                    where sub.id = '" + uuid_hex + "' \
                ) as target \
                where blocktable.height = target.height + (target.confirmation - 1)")
            time = str(cursor.fetchone()[0])
        finally:
            cursor.close()
        return time


    def as_dict(self):
        return OrderedDict([
            ('id', self.id),
            ('tx_hash', self.tx_hash),
            ('confirmation_count', self.confirmation_count),
            ('callback_url', self.callback_url),
            ('created_time', self.created_time)
        ])


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_time = models.DateTimeField(auto_now_add=True)
    is_notified = models.BooleanField(default=False, editable=False)
    notification_attempts = models.PositiveIntegerField(default=0, editable=False)
    notification_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class AddressNotification(Notification):
    subscription = models.ForeignKey('AddressSubscription')
    tx_hash = models.CharField(
        max_length=64,
        validators=[RegexValidator(r'^[0-9a-fA-F]{64}$')],
    )
    class Meta(Notification.Meta):
        ordering = ('created_time',)


class LastSeenBlock(models.Model):
    name = models.CharField(max_length=30)
    block_hash = models.CharField(
        max_length=64,
        validators=[RegexValidator(r'^[0-9a-fA-F]{64}$')],
    )


class TxNotification(Notification):
    subscription = models.ForeignKey('TxSubscription')

