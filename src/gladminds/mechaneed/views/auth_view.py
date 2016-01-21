from django.views.decorators.csrf import csrf_exempt
from provider.oauth2.models import Client
import json
import urllib
import urllib2
from gladminds.core.auth_helper import GmApps


@csrf_exempt
def get_access_token(user_auth, username, password, http_host):
    secret_cli = Client(user=user_auth, name='client', client_type=1, url='')
    secret_cli.save(using=GmApps.AFTERBUY)
    client_id = secret_cli.client_id
    client_secret = secret_cli.client_secret
    page = http_host + '/oauth2/access_token'
    if not 'http://' in page:
        page = 'http://' + page
    raw_params = {'client_id': client_id,
                  'client_secret': client_secret,
                  'grant_type': 'password',
                  'username': username,
                  'password': password,
                  'scope': 'write'
                  }
    params = urllib.urlencode(raw_params)
    oath_request = urllib2.Request(page, params)
    response = urllib2.urlopen(oath_request)
    return json.load(response)