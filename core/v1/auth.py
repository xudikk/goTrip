#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan

import datetime
import random

from django.conf import settings
from methodism import custom_response, code_decoder, exception_data, generate_key
import uuid

from base.helper import lang_helper
from base.errors import MSG
from core.models import Token, ExpiredToken, User, Otp


def auth_one(request, params):
    if 'phone' not in params:
        return custom_response(False, message=MSG['ParamsNotFull'][lang_helper(request)])
    if len(str(params['phone'])) != 12:
        return custom_response(False, message=MSG['LENPHONE'][lang_helper(request)])
    otp = random.randint(int(f'1{"0" * (settings.RANGE - 1)}'), int('9' * settings.RANGE))
    # shu yerda sms chiqib ketadi
    code = eval(settings.CUSTOM_HASHING)
    hash = code_decoder(code, l=settings.RANGE)
    token = Otp.objects.create(key=hash, mobile=params['phone'], step='one')

    return custom_response(True, data={
        "otp": otp,
        "token": token.key
    })


def resent_otp(request, params):
    if 'token' not in params: return custom_response(False, message=MSG['ParamsNotFull'][lang_helper(request)])
    otp = Otp.objects.filter(key=params['token']).first()
    if not otp: return custom_response(False, message=MSG['OTPTokenError'][lang_helper(request)])
    if otp.is_expired: return custom_response(False, message=MSG['OTPExpired'][lang_helper(request)])
    if otp.is_verified: return custom_response(False, message=MSG['TokenUnUsable'][lang_helper(request)])
    unhashed = code_decoder(otp.key, decode=True, l=settings.RANGE)
    code = eval(settings.UNHASH)
    # sms chiqib ketadi shu yerda
    return custom_response(True, data={
        "otp": int(code),
        "token": params['token']
    })


def auth_two(request, params):
    if 'otp' not in params or 'token' not in params:
        return custom_response(False, message=MSG['ParamsNotFull'][lang_helper(request)])
    otp = Otp.objects.filter(key=params['token']).first()
    if not otp: return custom_response(False, message=MSG['OTPTokenError'][lang_helper(request)])
    if otp.is_expired: return custom_response(False, message=MSG['OTPExpired'][lang_helper(request)])
    if (datetime.datetime.now() - otp.created).total_seconds() > 120:
        otp.step, otp.is_expired = 'two', True
        otp.save()
        return custom_response(False, message=MSG['OTPExpired'][lang_helper(request)])
    unhashed = code_decoder(otp.key, decode=True, l=settings.RANGE)
    code = eval(settings.UNHASH)
    if str(code) != str(params['otp']):
        otp.step, otp.tries = 'two', otp.tries + 1
        otp.save()
        return custom_response(False, message=MSG['OtpError'][lang_helper(request)])
    otp.is_verified, otp.is_expired = True, True
    user = User.objects.filter(phone=otp.mobile).first()
    otp.step = 'login' if user else 'regis'
    otp.save()
    return custom_response(True, data={'is_registered': user is not None})


def regis(request, params):
    if 'phone' not in params or 'password' not in params or "token" not in params:
        return custom_response(False, message=MSG['ParamsNotFull'][lang_helper(request)])

    # check otp
    otp = Otp.objects.filter(key=params['token']).first()
    if not otp: return custom_response(False, message=MSG['OTPTokenError'][lang_helper(request)])
    if otp.step != 'regis': return custom_response(False, message=MSG['TokenUnUsable'][lang_helper(request)])
    if not otp.is_verified: return custom_response(False, message=MSG['TokenUnUsable'][lang_helper(request)])
    if (datetime.datetime.now() - otp.created).total_seconds() > 180:
        otp.is_expired = True
        otp.save()
        return custom_response(False, message=MSG['OTPExpired'][lang_helper(request)])
    data = {'phone': params['phone'], 'password': params['password'], 'first_name': params.get('first_name', ''),
            'last_name': params.get('last_name', ''), 'email': params.get('email', ''), 'avatar': 'avatar'}
    user = User.objects.create_user(**data)

    # create fixtures
    token = Token.objects.create(user=user)
    otp.step, user.last_login = 'registered', datetime.datetime.now()
    otp.save()
    user.save()
    return custom_response(status=True, data={'access_token': token.key, 'mobile': user.phone},
                           message=MSG['Success'][lang_helper(request)])


def login(request, params):
    if "phone" not in params or 'password' not in params or "token" not in params:
        return custom_response(False, message=MSG['ParamsNotFull'][lang_helper(request)])

    # otp check
    otp = Otp.objects.filter(key=params['token']).first()
    if not otp: return custom_response(False, message=MSG['OTPTokenError'][lang_helper(request)])
    if otp.step != 'login': return custom_response(False, message=MSG['TokenUnUsable'][lang_helper(request)])
    if not otp.is_verified: return custom_response(False, message=MSG['TokenUnUsable'][lang_helper(request)])
    if otp.mobile != str(params['phone']): return custom_response(False, message=MSG['OTPPhoneAndPhoneNotMatch'][
        lang_helper(request)])

    # user check
    user = User.objects.filter(phone=params['phone']).first()
    if not user: return custom_response(False, MSG['UserNot'][lang_helper(request)])
    if not user.is_active: return custom_response(False, message=MSG['UserDeleted'][lang_helper(request)])
    if not user.check_password(params['password']): return custom_response(False,
                                                                           MSG['PasswordError'][lang_helper(request)])
    token = Token.objects.get_or_create(user=user)[0]
    user.last_login = datetime.datetime.now()
    user.save()
    return custom_response(True, data={"token": token.key})


def logout(request):
    token = Token.objects.filter(user=request.user).first()
    if token:
        ExpiredToken.objects.create(user=token.user, key=token.key)
        token.delete()
    return custom_response(True, message=MSG['LoggedOut'][lang_helper(request)])
