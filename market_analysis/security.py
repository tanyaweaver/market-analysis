import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy.exc import DBAPIError
from pyramid.session import SignedCookieSessionFactory  # for CSRF security

from .models import Users


class MyRoot(object):
    '''custom root providds app-levelpermissions'''

    def __init__(self, request):
        self.request = request

    def __acl__(self):
        base_list = [
            (Allow, Everyone, 'view'),
            (Allow, Authenticated, 'secret'),
        ]
        # import pdb; pdb.set_trace()
        if self.request.authenticated_userid:
            current_user = self.request.dbsession.query(Users).filter(
                Users.username == self.request.authenticated_userid
            ).first()
            if current_user and current_user.is_admin:
                base_list.append((Allow, self.request.authenticated_userid,
                                 'admin'))
        return base_list


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
    # Bellow added for CSRF
    session_secret = os.environ.get('SESSION_SECRET', '')
    session_factory = SignedCookieSessionFactory(session_secret)
    config.set_session_factory(session_factory)
    config.set_default_csrf_options(require_csrf=True)


def check_credentials(request, username, password):
    is_auth = False
    try:
        query = request.dbsession.query(Users)
        user_data = query.filter_by(username=username).first()
    except DBAPIError:
        return is_auth
    if user_data:
        stored_password = user_data.pass_hash
        try:
            is_auth = pwd_context.verify(password, stored_password)
        except ValueError:
            pass
    return is_auth
