#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan

from methodism import METHODISM, method_and_params_checker, custom_response, MESSAGE, exception_data
from re import compile as re_compile

from rest_framework.response import Response

from base.helper import lang_helper


class CustomMETHODISM(METHODISM):

    @method_and_params_checker
    def post(self, requests, *args, **kwargs):
        method = requests.data.get("method")
        params = requests.data.get("params")
        headers = requests.headers
        if method not in self.not_auth_methods and "*" not in self.not_auth_methods:
            authorization = headers.get(self.auth_headers, '')
            pattern = re_compile(self.token_key + r" (.+)")

            if not pattern.match(authorization):
                return Response(custom_response(status=False, method=method, message=MESSAGE['NotAuthenticated'][lang_helper(requests)]))
            input_token = pattern.findall(authorization)[0]

            # Authorize
            token = self.token_class.objects.filter(key=input_token).first()
            if not token:
                return Response(custom_response(status=False, method=method, message=MESSAGE['AuthToken'][lang_helper(requests)]))
            requests.user = token.user
        try:
            funk = getattr(self.file, method.replace('.', '_').replace('-', '_'))
        except AttributeError:
            return Response(custom_response(False, method=method, message=MESSAGE['MethodDoesNotExist'][lang_helper(requests)]))
        except Exception as e:
            return Response(custom_response(False, method=method, message=MESSAGE['UndefinedError'][lang_helper(requests)],
                                            data=exception_data(e)))
        res = map(funk, [requests], [params])
        try:
            response = Response(list(res)[0])
            response.data.update({'method': method})
        except Exception as e:
            response = Response(custom_response(False, method=method, message=MESSAGE['UndefinedError'][lang_helper(requests)],
                                                data=exception_data(e)))
        return response

