from pyramid.response import Response

from server import API_KEY


def requires_api_key(view_callable):
    def inner(context, request):
        if request.headers.get('x-api-key') == API_KEY:
            return view_callable(context, request)
        else:
            return Response('No valid API Key provided', status='401')
    return inner
