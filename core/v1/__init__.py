#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan
from methodism.helper import custom_response as cr

from .auth import login, auth_one, auth_two, regis, resent_otp
from .settings import set_lang, check_pass, change_pass, user_edit


""" Method Names Getter """

unusable_method = dir()


def method_names(requests):
    return cr(True, data=[x.replace('_', '.') for x in unusable_method if '__' not in x and x != 'cr'])

