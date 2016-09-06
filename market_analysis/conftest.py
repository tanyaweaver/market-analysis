from webtest import TestApp as _Test_App
# import os
import pytest
from pyramid import testing
from .models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from .models.meta import Base
import transaction

# import datetime
from .models.mymodel import Users
from passlib.apps import custom_app_context as pwd_context


DB_SETTINGS = {'sqlalchemy.url': 'sqlite:///:memory:'}


@pytest.fixture(scope='session')
def sqlengine(request):
    config = testing.setUp(settings=DB_SETTINGS)
    config.include('.models')
    settings = config.get_settings()
    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    def teardown():
        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return engine


@pytest.fixture(scope='function')
def new_session_scope_function(sqlengine, request):
    session_factory = get_session_factory(sqlengine)
    dbsession = get_tm_session(session_factory, transaction.manager)

    def teardown():
        transaction.abort()

    request.addfinalizer(teardown)
    return dbsession


@pytest.fixture(scope='session')
def new_session_scope_session(sqlengine, request):
    session_factory = get_session_factory(sqlengine)
    dbsession = get_tm_session(session_factory, transaction.manager)

    user = Users(username='fake', pass_hash=pwd_context.encrypt('fake'))
    dbsession.add(user)
    dbsession.flush()
    import pdb; pdb.set_trace()

    def teardown():
        transaction.abort()

    request.addfinalizer(teardown)
    return dbsession


@pytest.fixture()
def app(new_session_scope_session):
    '''testapp fixture'''
    from market_analysis import main
    app = main({}, **DB_SETTINGS)
    from webtest import TestApp
    return TestApp(app)


@pytest.fixture(scope="function")
def authenticated_app(app, new_session):
    user = Users(username='fake', pass_hash=pwd_context.encrypt('fake'))
    new_session.add(user)
    new_session.flush()
    actual_username = 'fake'
    actual_password = 'fake'
    auth_data = {
        'username': actual_username,
        'password': actual_password,
    }
    response = app.post('/login', auth_data, status='3*')
    return app

# PASSWORD = 'secret password'
# ENCRYPTED_PASSWORD = pwd_context.encrypt(PASSWORD)
#
#
# @pytest.fixture(scope='function')
# def auth_env():
#     username = 'banksd'
#     os.environ['AUTH_USERNAME'] = username
#     os.environ['AUTH_PASSWORD'] = ENCRYPTED_PASSWORD
#
#     return username, PASSWORD
# #
# #
# @pytest.fixture(scope="function")
# def authenticated_app(auth_env, new_session):
#     app, token = app_and_csrf_token
#     actual_username, actual_password = auth_env
#     auth_data = {'username': actual_username,
#                  'password': actual_password,
#                  'csrf_token': token}
#     response = app.post('/login', auth_data, status='3*')
#     return app
