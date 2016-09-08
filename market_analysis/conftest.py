from webtest import TestApp as _Test_App
import os
import pytest
from pyramid import testing
from .models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from .models.meta import Base
import transaction
from market_analysis.scripts.test_db import STOCKS_100
# import datetime
from .models.mymodel import Users, Association, Stocks
from passlib.apps import custom_app_context as pwd_context


OS_USER = os.environ.get('USER', 'tatianaphillips')
DB_SETTINGS = {'sqlalchemy.url': 'postgres://{}:@localhost:5432/testing'.format(OS_USER)}


@pytest.fixture(scope='session')
def sqlengine(request):
    config = testing.setUp(settings=DB_SETTINGS)
    config.include('.models')
    config.testing_securitypolicy(userid='fake', permissive=True)
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
def new_session(sqlengine, request):
    session_factory = get_session_factory(sqlengine)
    dbsession = get_tm_session(session_factory, transaction.manager)

    def teardown():
        transaction.abort()

    request.addfinalizer(teardown)
    return dbsession


@pytest.fixture(scope='session')
def populated_db(sqlengine, request):
    session_factory = get_session_factory(sqlengine)
    dbsession = get_tm_session(session_factory, transaction.manager)

    with transaction.manager:
        user = Users(
            username=USER_CREDENTIALS['username'],
            pass_hash=pwd_context.encrypt(USER_CREDENTIALS['password']))
        dbsession.add(user)
        
        # import pdb; pdb.set_trace()
        for line in STOCKS_100:
            stock = Stocks(symbol=line[0], name=line[1], exchange='NASDAQ')
            dbsession.add(stock)
            
        association_test = [
                        (1, 1, 10),
                        (1, 2, 10),
                        (1, 3, 10),
                        (1, 4, 13),
                        (1, 5, 12),
                        ]
        for tup in association_test:
            association = Association(user_id=tup[0], stock_id=tup[1], shares=tup[2])
            dbsession.add(association)


        def teardown():
            with transaction.manager:
                dbsession.query(Association).delete()
                dbsession.query(Users).delete()
                dbsession.query(Stocks).delete()
            

    request.addfinalizer(teardown)


@pytest.fixture(scope='session')
def populated_db_admin(sqlengine, request):
    session_factory = get_session_factory(sqlengine)
    dbsession = get_tm_session(session_factory, transaction.manager)

    with transaction.manager:
        user = Users(
            username=ADMIN_CREDENTIALS['username'],
            pass_hash=pwd_context.encrypt(ADMIN_CREDENTIALS['password']),
            is_admin=1)
        dbsession.add(user)
        # import pdb; pdb.set_trace()

    def teardown():
        with transaction.manager:
            dbsession.query(Users).delete()

    request.addfinalizer(teardown)


USER_CREDENTIALS = {'username': 'fake', 'password': 'fake'}
ADMIN_CREDENTIALS = {'username': 'admin', 'password': 'admin'}


@pytest.fixture()
def app():
    '''testapp fixture'''
    from market_analysis import main
    app = main({}, **DB_SETTINGS)
    from webtest import TestApp
    return TestApp(app)


@pytest.fixture(scope="function")
def auth_app(app_and_csrf_token, populated_db):
    app, token = app_and_csrf_token
    auth_data = {
        'username': USER_CREDENTIALS['username'],
        'password': USER_CREDENTIALS['password'],
        'csrf_token': token,
    }
    response = app.post('/login', auth_data, status='3*')
    return app


@pytest.fixture(scope="function")
def admin_app(app_and_csrf_token, populated_db_admin):
    app, token = app_and_csrf_token
    auth_data = {
        'username': ADMIN_CREDENTIALS['username'],
        'password': ADMIN_CREDENTIALS['password'],
        'csrf_token': token,
    }
    response = app.post('/login', auth_data, status='3*')
    return app, token


@pytest.fixture(scope='function')
def app_and_csrf_token(app):
    response = app.get('/login')
    # import pdb; pdb.set_trace()
    input_ = response.html.find('input', attrs={'name': 'csrf_token'})
    token = input_.attrs['value']
    return app, token

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
