import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Everyone
from pyramid.security import Allow

# def check_credentials(username, password):
#     stored_username =


class MyRoot(object):
    '''custom root providds app-levelpermissions'''

    def __init__(self, request):
        self.request = request

        __acl__ = [
            (Allow, Everyone, 'view'),
        ]


def includeme(config):
    '''security-related configuration'''
    auth_secret = os.environ.get('AUTH_SECRET', '')
    authn_policy = AuthTktAuthenticationPolicy(
        secret=auth_secret,
        hashalg='sha512'
    )
    config.set_authentication_policy(authn_policy)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)
    config.set_default_permission('view')
