#  Created by Xudoyberdi Egamberdiyev
#
#  Please contact before making any changes
#
#  Tashkent, Uzbekistan

def lang_helper(request):
    if not request.user.is_anonymous:
        return request.user.lang
    return 'uz'
