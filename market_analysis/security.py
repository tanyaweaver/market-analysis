import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.exc import DBAPIError

from .models import Users

# def check_credentials(username, password):
#     stored_username =


class MyRoot(object):
    '''custom root providds app-levelpermissions'''

    def __init__(self, request):
        self.request = request

    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'secret')
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
    config.set_root_factory(MyRoot)


def check_credentials(request, username, password):
    is_auth = False
    try:
        query = request.dbsession.query(Users)
        user_data = query.filter_by(user=request.matchdict['username']).first()
        stored_password = user_data['pass_hash']
    except DBAPIError:
        return is_auth
    if stored_password:
        try:
            is_auth = pwd_context.verify(password, stored_password)
        except ValueError:
            pass
    return is_auth
