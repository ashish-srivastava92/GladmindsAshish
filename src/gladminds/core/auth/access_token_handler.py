from django.conf import settings
from django.utils import timezone

from provider.oauth2.models import Client, AccessToken
from gladminds.core.exceptions import AuthError
import logging


def create_access_token(user_auth, http_host):
    '''
    Used for creating access token
    :param user_auth:
    :type user_auth:
    :param http_host:
    :type http_host:
    '''
    secret_cli = Client(user=user_auth, name='client', client_type=1, url='')
    secret_cli.save(using=settings.BRAND)

    access_token = AccessToken(
        user=user_auth,
        client=secret_cli,
        scope=6
    )
    AccessToken.objects.filter(user=user_auth, client=secret_cli,
                               scope=6).using(settings.BRAND).delete()
    access_token.save(using=settings.BRAND)
    return access_token.token


def verify_access_token(key, user=None):
    '''
    FOr verifying acess token
    :param key:
    :type key:
    :param user:
    :type user:
    '''
    if  (settings.ENV in settings.IGNORE_ENV and key in settings.HARCODED_TOKEN):
        return key
    try:
        token = AccessToken.objects.using(settings.BRAND).get(token=key) 
        # Check if token has expired
        if token.expires < timezone.now():
            raise AuthError('AccessToken has expired.')
    except AccessToken.DoesNotExist, e:
        try:
            token =  AccessToken.objects.using('afterbuy').get(token=key)
        except AccessToken.DoesNotExist, e:
            try:
                token =  AccessToken.objects.using('bajaj').get(token=key)
            except AccessToken.DoesNotExist, e:
                logging.info('InValid access : {0}'.format(e))
                raise AuthError('AccessToken not found at all.')
    logging.info('Valid access')
    return token


def delete_access_token(access_token):
    '''
    Deletes access token
    :param access_token:
    :type access_token:
    '''
    AccessToken.objects.using(settings.BRAND).get(token=
                                                     access_token).delete()
