#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan
from django.conf import settings
from methodism import custom_response, MESSAGE, exception_data
from re import compile as re_compile

from rest_framework.response import Response

from base.custom import CustomMETHODISM, method_checker
from base.helper import lang_helper
from core.models.tokens import Token
from core import v1
from core.v1 import get_methods


class GTMain(CustomMETHODISM):
    file = v1
    token_key = "GoBearer"
    auth_headers = 'GoTrip-Authorization'
    token_class = Token
    not_auth_methods = settings.METHODS
    get_methods = get_methods

    @method_checker
    def get(self, request, *args, **kwargs):
        method = request.GET.get("method")
        headers = request.headers
        if method not in self.not_auth_methods and "*" not in self.not_auth_methods:
            authorization = headers.get(self.auth_headers, '')
            pattern = re_compile(self.token_key + r" (.+)")

            if not pattern.match(authorization):
                return Response(custom_response(status=False, method=method, message=MESSAGE['NotAuthenticated'][lang_helper(request)]))
            input_token = pattern.findall(authorization)[0]

            # Authorize
            token = self.token_class.objects.filter(key=input_token).first()
            if not token:
                return Response(custom_response(status=False, method=method, message=MESSAGE['AuthToken'][lang_helper(request)]))
            request.user = token.user
        try:
            funk = getattr(self.get_methods, method.replace('.', '_').replace('-', '_'))
        except AttributeError:
            return Response(custom_response(False, method=method, message=MESSAGE['MethodDoesNotExist'][lang_helper(request)]))
        except Exception as e:
            return Response(custom_response(False, method=method, message=MESSAGE['UndefinedError'][lang_helper(request)],
                                            data=exception_data(e)))
        res = map(funk, [request])
        try:
            response = Response(list(res)[0])
            response.data.update({'method': method})
        except Exception as e:
            response = Response(custom_response(False, method=method, message=MESSAGE['UndefinedError'][lang_helper(request)],
                                                data=exception_data(e)))
        return response
