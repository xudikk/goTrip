#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan
from methodism.main import METHODISM, SqlAPIMethodism

from core.models.tokens import Token


class GTMain(METHODISM):
    file = "__main__"
    token_key = "GoBearer"
    auth_headers = 'GoTrip-Authorization'
    token_class = Token
    not_auth_methods = ['*']

