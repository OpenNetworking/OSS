from __future__ import unicode_literals

from django.db import models


class Address(models.Model):
    address = models.CharField(unique=True, max_length=40)


class Block(models.Model):
    hash = models.CharField(unique=True, max_length=32)
    height = models.DecimalField(max_digits=14, decimal_places=0, blank=True, null=True)
    prev_block = models.ForeignKey('self', blank=True, null=True,
                                   related_name='next_blocks', related_query_name='next_block')
    merkle_root = models.CharField(max_length=32, blank=True, null=True)
    time = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)
    bits = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    nonce = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    version = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    in_longest = models.DecimalField(max_digits=1, decimal_places=0, blank=True, null=True)
    size = models.DecimalField(max_digits=14, decimal_places=0, blank=True, null=True)
    chain_work = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)
    tx_count = models.DecimalField(max_digits=10, decimal_places=0)

    @property
    def confirmation(self):
        # orphan
        if not self.in_longest:
            return 0
        # main branch
        else:
            max_height = Block.objects.filter(in_longest=1).count()
            return int(max_height - self.height) + 1


class Datadir(models.Model):
    dirname = models.CharField(max_length=2000)
    blkfile_number = models.DecimalField(max_digits=8, decimal_places=0, blank=True, null=True)
    blkfile_offset = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)


class Tx(models.Model):
    TX_TYPE = {
        0: 'NORMAL',
        1: 'MINT',
        2: 'LICENSE',
        3: 'VOTE',
        4: 'BANVOTE',
        5: 'MATCH',
        6: 'CANCEL',
    }

    hash = models.CharField(unique=True, max_length=32)
    block = models.ForeignKey(Block, related_name='txs', related_query_name='tx')
    version = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    locktime = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    type = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    size = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    time = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)


class TxOut(models.Model):
    tx = models.ForeignKey(Tx, related_name='tx_outs', related_query_name='tx_out')
    value = models.DecimalField(max_digits=30, decimal_places=0)
    position = models.DecimalField(max_digits=10, decimal_places=0)
    scriptpubkey = models.BinaryField(blank=True, null=True)
    address = models.ForeignKey(Address, related_name='tx_outs', related_query_name='tx_out')
    spent = models.DecimalField(max_digits=1, decimal_places=0, blank=True, null=True)
    color = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)


class TxIn(models.Model):
    tx = models.ForeignKey(Tx, related_name='tx_ins', related_query_name='tx_in')
    txout = models.ForeignKey(TxOut, related_name='tx_ins', related_query_name='tx_in')
    position = models.DecimalField(max_digits=10, decimal_places=0)
    scriptsig = models.BinaryField(blank=True, null=True)
    sequence = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)

