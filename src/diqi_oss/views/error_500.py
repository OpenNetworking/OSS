import httplib

from django.http import JsonResponse


def server_error(request):
    response = {'error': 'internal server error'}
    return JsonResponse(response, status=httplib.INTERNAL_SERVER_ERROR)
