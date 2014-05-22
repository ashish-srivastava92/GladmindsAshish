from django.contrib.auth.models import AnonymousUser, User
from django.utils import timezone
from tastypie.authentication import Authentication
from provider.oauth2.models import AccessToken
import logging


class AuthError(RuntimeError):
    '''
    General exception class.
    '''
    def __init__(self, message='OAuth error occured.'):
        self.message = message


class AccessTokenAuthentication(Authentication):
    
    def is_authenticated(self, request, **kwargs):
        try:
            access_token_container = request.GET.urlencode().split('accessToken=')[1]
            key = access_token_container.split('&')[0]
            if not key:
                logging.error('AccessTokenAuthentication. No Access Token found.')
                return None
            '''
            If verify_access_token() does not pass, it will raise an error
            '''
            self.verify_access_token(key)
            return True
        except KeyError, e:
            logging.exception('Error in Authentication. {0}'.format(e))
            request.user = AnonymousUser()
            return False
        except Exception, e:
            logging.exception('Error in Authentication. {0}'.format(e))
            return False
        return True
    
    def verify_access_token(self, key):
        try:
            token = AccessToken.objects.get(token=key)
            # Check if token has expired
            if token.expires < timezone.now():
                raise AuthError('AccessToken has expired.')
        except AccessToken.DoesNotExist, e:
            logging.info('InValid access : {0}'.format(e))
            raise AuthError('AccessToken not found at all.')
    
        logging.info('Valid access')
        return token