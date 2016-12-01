import httplib
import logging

from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from gcoin import (encode_license, make_mint_raw_tx, make_raw_tx,
                   mk_op_return_script)
from gcoinrpc import connect_to_remote
from gcoinrpc.exceptions import InvalidAddressOrKey, InvalidParameter

from ..utils import balance_from_utxos, select_utxo, utxo_to_txin
from .forms import *

logger = logging.getLogger(__name__)


def get_rpc_connection():
    return connect_to_remote(settings.GCOIN_RPC['user'],
                             settings.GCOIN_RPC['password'],
                             settings.GCOIN_RPC['host'],
                             settings.GCOIN_RPC['port'])


def server_error(request):
    response = {"error": "internal server error"}
    return JsonResponse(response, status=httplib.INTERNAL_SERVER_ERROR)


class CsrfExemptMixin(object):
    """
    Exempts the view from CSRF requirements.

    This should be the left-most mixin of a view.
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CsrfExemptMixin, self).dispatch(*args, **kwargs)


class GetLicenseInfoView(View):

    def get(self, request, color_id, *args, **kwargs):
        try:
            response = get_rpc_connection().getlicenseinfo(int(color_id))
            # change some dictionary key names
            response['total_amount'] = response.pop('Total amount')
            response['owner'] = response.pop('Owner')
            return JsonResponse(response)
        except InvalidParameter:
            response = {'error': 'license color not exist'}
            return JsonResponse(response, status=httplib.NOT_FOUND)


class CreateLicenseRawTxView(View):

    def __init__(self):
        super(CreateLicenseRawTxView, self).__init__()
        self._conn = get_rpc_connection()
        self.TX_LICENSE_TYPE = 2

    def get(self, request):
        form = CreateLicenseRawTxForm(request.GET)
        if form.is_valid():
            color_id = form.cleaned_data['color_id']
            to_address = form.cleaned_data['to_address']
            alliance_member_address = form.cleaned_data['alliance_member_address']

            if self._is_license_created(color_id):
                return JsonResponse({'error': 'license with such color already exists'}, status=httplib.BAD_REQUEST)

            color_0_utxo = self._find_color_0_utxo(alliance_member_address)
            if not color_0_utxo:
                return JsonResponse({'error': 'insufficient color 0 in alliance member address'}, status=httplib.BAD_REQUEST)

            color_0_tx_ins = [utxo_to_txin(color_0_utxo)]

            license_script = self._get_license_script(form.cleaned_data)
            license_info_tx_outs = [
                {'address': to_address, 'value': int(10**8), 'color': color_id},
                {'script': license_script, 'value': 0, 'color': color_id}
            ]

            create_license_raw_tx = make_raw_tx(
                color_0_tx_ins,
                license_info_tx_outs,
                self.TX_LICENSE_TYPE
            )

            return JsonResponse({'raw_tx': create_license_raw_tx})
        else:
            errors = ', '.join(reduce(lambda x, y: x + y, form.errors.values()))
            response = {'error': errors}
            return JsonResponse(response, status=httplib.BAD_REQUEST)

    def _is_license_created(self, color_id):
        try:
            self._conn.getlicenseinfo(int(color_id))
            return True
        except InvalidParameter:
            return False

    def _find_color_0_utxo(self, alliance_member_address):
        utxos = self._conn.gettxoutaddress(alliance_member_address)
        inputs = select_utxo(utxos=utxos, color=0, sum=1)
        return inputs[0] if inputs else None

    def _get_license_script(self, data):
        license = {
            'name': data['name'],
            'description': data['description'],
            'issuer': 'none',
            'fee_collector': 'none',
            'member_control': data['member_control'],
            'metadata_link': data['metadata_link'],
            'upper_limit': data['upper_limit'] or 0,
        }

        license_hex = encode_license(license)
        return mk_op_return_script(license_hex)


class GetRawTxView(View):

    def get(self, request, tx_id, *args, **kwargs):
        try:
            response = get_rpc_connection().getrawtransaction(tx_id)
            return JsonResponse(response.__dict__)
        except (InvalidParameter, InvalidAddressOrKey):
            response = {'error': 'transaction not found'}
            return JsonResponse(response, status=httplib.NOT_FOUND)


class CreateRawTxView(CsrfExemptMixin, View):

    def post(self, request, *args, **kwargs):
        form = RawTxForm(request.POST)

        if not form.is_valid():
            errors = ', '.join(reduce(lambda x, y: x + y, form.errors.values()))
            response = {'error': errors}
            return JsonResponse(response, status=httplib.BAD_REQUEST)

        from_address = form.cleaned_data['from_address']
        to_address = form.cleaned_data['to_address']
        color_id = form.cleaned_data['color_id']
        amount = form.cleaned_data['amount']
        op_return_data = form.cleaned_data['op_return_data']
        fee = form.cleaned_data['fee'] or 1

        utxos = get_rpc_connection().gettxoutaddress(from_address)

        # Check if there's sufficient amount of `color_id`.
        inputs = select_utxo(utxos, color_id, amount)
        if not inputs and amount != 0:
            return JsonResponse({'error': 'insufficient funds'}, status=httplib.BAD_REQUEST)

        # Check if there's sufficient fee.
        if color_id == 1:
            # We have to include `amount` here so we don't have duplicated utxos.
            fee_inputs = select_utxo(utxos, 1, amount + fee)
        else:
            fee_inputs = select_utxo(utxos, 1, fee)
        if not fee_inputs:
            return JsonResponse({'error': 'insufficient fee'}, status=httplib.BAD_REQUEST)

        # Add fee utxo to input
        if color_id == 1:
            inputs = fee_inputs
        else:
            inputs += fee_inputs

        ins = [utxo_to_txin(utxo) for utxo in inputs]
        outs = [{'address': to_address, 'value': int(amount * 10**8), 'color': color_id}]

        # Now for the `change` part.
        if color_id == 1:
            inputs_value = balance_from_utxos(inputs)[color_id]
            change = inputs_value - (amount + fee)
            if change:
                outs.append({'address': from_address,
                             'value': int(change * 10**8), 'color': color_id})
        else:
            inputs_value = balance_from_utxos(inputs).get(color_id, 0)
            change = inputs_value - amount
            if change:
                outs.append({'address': from_address,
                             'value': int(change * 10**8), 'color': color_id})
            # Fee `change`.
            color1_value = balance_from_utxos(inputs)[1]
            fee_change = color1_value - fee
            if fee_change:
                outs.append({'address': from_address,
                             'value': int(fee_change * 10**8), 'color': 1})

        if op_return_data:
            outs.append({
                'script': mk_op_return_script(op_return_data.encode('utf8')),
                'value': 0,
                'color': 0
            })
            raw_tx = make_raw_tx(ins, outs, 5)  # contract type
        else:
            raw_tx = make_raw_tx(ins, outs)

        return JsonResponse({'raw_tx': raw_tx})


class SendRawTxView(CsrfExemptMixin, View):

    def post(self, request, *args, **kwargs):
        raw_tx = request.POST.get('raw_tx', '')
        try:
            tx_id = get_rpc_connection().sendrawtransaction(raw_tx)
            response = {'tx_id': tx_id}
            return JsonResponse(response)
        except:
            logger.error('Invalid transaction: %s', raw_tx, exc_info=True)
            response = {'error': 'invalid raw transaction'}
            return JsonResponse(response, status=httplib.BAD_REQUEST)


class GetBalanceView(View):

    def get(self, request, address, *args, **kwargs):
        utxos = get_rpc_connection().gettxoutaddress(address)
        balance_dict = balance_from_utxos(utxos)
        return JsonResponse(balance_dict)


class CreateMintRawTxView(View):

    def get(self, request, *args, **kwargs):
        form = MintRawTxForm(request.GET)
        if form.is_valid():
            mint_address = form.cleaned_data['mint_address']
            color_id = form.cleaned_data['color_id']
            amount = form.cleaned_data['amount']

            raw_tx = make_mint_raw_tx(mint_address, color_id, int(amount * 10**8))
            return JsonResponse({'raw_tx': raw_tx})
        else:
            errors = ', '.join(reduce(lambda x, y: x + y, form.errors.values()))
            response = {'error': errors}
            return JsonResponse(response, status=httplib.BAD_REQUEST)


class CreateLicenseTransferRawTxView(View):

    def get(self, request, *args, **kwargs):
        form = CreateLicenseTransferRawTxForm(request.GET)
        if form.is_valid():
            from_address = form.cleaned_data['from_address']
            to_address = form.cleaned_data['to_address']
            color_id = form.cleaned_data['color_id']

            utxos = get_rpc_connection().gettxoutaddress(from_address, True, 1)
            utxo = self._get_license_utxo(utxos, color_id)
            if not utxo:
                return JsonResponse({'error': 'insufficient funds'}, status=httplib.BAD_REQUEST)

            ins = [utxo_to_txin(utxo)]
            outs = [{'address': to_address, 'value': 100000000, 'color': color_id}]

            raw_tx = make_raw_tx(ins, outs, 2)
            return JsonResponse({'raw_tx': raw_tx})
        else:
            errors = ', '.join(reduce(lambda x, y: x + y, form.errors.values()))
            response = {'error': errors}
            return JsonResponse(response, status=httplib.BAD_REQUEST)

    def _get_license_utxo(self, utxos, color):
        for utxo in utxos:
            if utxo['color'] == color:
                return utxo
        return None
