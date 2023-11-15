from urllib.parse import urlencode

from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken


def exchange_token(strategy, user, *args, **kwargs):
    redirect_url = getattr(settings, 'CLIENT_LOGIN_REDIRECT_URL', None)
    if user and user.is_active():
        token = RefreshToken.for_user(user)
        query = urlencode({
            'access_token': str(token.access_token),
            'refresh_token': str(token),
        })
        redirect_url = f'{redirect_url}?{query}'

    return strategy.redirect(redirect_url)
