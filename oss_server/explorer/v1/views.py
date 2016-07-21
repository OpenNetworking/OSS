import httplib

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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


class GetColorTxsView(View):
    def get(self, request, color_id):
        tx_list = Tx.objects.filter(tx_out__color=color_id, type__lte=1).distinct()
        tx_list = [tx.as_dict() for tx in tx_list]
        paginator = Paginator(tx_list, 50)

        # deliver first page if page is not given
        if 'page' in request.GET:
            page = request.GET['page']
        else:
            page = 1

        try:
            txs = paginator.page(page)
        except PageNotAnInteger:
            # deliver first page if page is not an integer
            txs = paginator.page(1)
            page = 1
        except EmptyPage:
            # deliver last page if page is out of range
            txs = paginator.page(paginator.num_pages)
            page = paginator.num_pages

        response = {'page': page, 'txs': txs.object_list}
        return JsonResponse(response)

