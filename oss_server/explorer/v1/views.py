import httplib

from django.http import JsonResponse
from django.views.generic import View

from ..models import *


class GetLatestBlocksView(View):
    def get(self, request):
        latest_blocks = Block.objects.filter(in_longest=1)[:50]
        response = {'blocks': [block.as_dict() for block in latest_blocks]}
        return JsonResponse(response)


class GetBlockByHashView(View):
    def get(self, request, block_hash):
        try:
            response = {'block': Block.objects.get(hash=block_hash).as_dict()}
            return JsonResponse(response)
        except Block.DoesNotExist:
            response = {'error': 'block not exist'}
            return JsonResponse(response, status=httplib.NOT_FOUND)


class GetBlockByHeightView(View):
    def get(self, request, block_height):
        try:
            response = {'block': Block.objects.get(height=block_height, in_longest=1).as_dict()}
            return JsonResponse(response)
        except Block.DoesNotExist:
            response = {'error': 'block not exist'}
            return JsonResponse(response, status=httplib.NOT_FOUND)


class GetTxByHashView(View):
    def get(self, request, tx_hash):
        try:
            response = {'tx': Tx.objects.get(hash=tx_hash).as_dict()}
            return JsonResponse(response)
        except Tx.DoesNotExist:
            response = {'error': 'tx not exist'}
            return JsonResponse(response, status=httplib.NOT_FOUND)
