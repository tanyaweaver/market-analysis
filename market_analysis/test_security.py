from .models import Users
from .conftest import USER_CREDENTIALS
# import os
# from pyramid import testing


def test_public_view(app):
    response = app.get('/public', status='2*')
    assert response.status_code == 200


def test_private_view(app):
    response = app.get('/private', status='4*')
    assert response.status_code == 403


def test_user_db_exists(new_session):
    assert len(new_session.query(Users).all()) == 0


def test_user_gets_added_to_db(new_session):
    user = Users(username=USER_CREDENTIALS['username'], pass_hash='hashiehas')
    new_session.add(user)
    new_session.flush()
    assert len(new_session.query(Users).all()) == 1


def test_login_view_is_public(app):
    response = app.get('/login', status='2*')
    assert response.status_code == 200


def test_login_correct_user_info(app_and_csrf_token, populated_db):
    '''Checks the POST form submital for correct user login data'''
    # import pdb; pdb.set_trace()
    app, token = app_and_csrf_token
    auth_data = {'username': 'fake',
                 'password': 'fake',
                 'csrf_token': token}
    response = app.post('/login', auth_data, status='3*')
    assert response.status_code == 302


def test_login_bad_user_info(app_and_csrf_token, populated_db):
    '''Checks the POST form submital for correct user login data'''
    # import pdb; pdb.set_trace()
    app, token = app_and_csrf_token
    auth_data = {'username': 'fake',
                 'password': 'not the correct password',
                 'csrf_token': token}
    response = app.post('/login', auth_data, status='2*')
    # import pdb; pdb.set_trace()
    assert b"Username or Password Not Recognized" in response.body


def test_private_view_access_to_authenticated(auth_app, populated_db):
    response = auth_app.get('/private', status='2*')
    assert response.status_code == 200


def test_createnewuser_view_is_public(app):
    response = app.get('/new_user', status='2*')
    assert response.status_code == 200


def test_logout(app):
    response = app.get('/logout', status="3*")
    assert response.status_code == 302


def test_home_public(app):
    response = app.get('/', status="3*")
    assert response.status_code == 302


def test_home_rederects_to_portfolio(auth_app, populated_db):
    response = auth_app.get('/', status='3*')
    assert response.status_code == 302


def test_admin_is_private(app):
    response = app.get('/admin', status='4*')
    assert response.status_code == 403


def test_admin_accessable_to_adim(admin_app, populated_db_admin):
    app, token = admin_app
    # response = admin_app.get('/admin', status='2*')
    response = app.get('/admin', status='2*')
    assert response.status_code == 200


def test_admin_not_accessable_to_non_admin(auth_app, populated_db):
    response = auth_app.get('/admin', status='4*')
    assert response.status_code == 403


def test_admin_delet_post_request_csrf(admin_app, populated_db):
    '''Checks admin view POST for correct CSRF Token'''
    # import pdb; pdb.set_trace()
    app, token = admin_app
    auth_data = {'username': 'fake',
                 'csrf_token': token}
    response = app.post('/admin', auth_data, status='2*')
    assert response.status_code == 200


def test_new_user_is_public(app):
    response = app.get('/new_user', status="2*")
    assert response.status_code == 200


def test_new_user_post_missing_field(app_and_csrf_token, populated_db):
    '''Checks the POST form missing fields'''
    app, token = app_and_csrf_token
    auth_data = {'username': '',
                 'password': 'fdsafdsa',
                 'password_verify': 'fdsafda',
                 'last_name': 'Smith',
                 'first_name': 'Zeek',
                 'email': 'fdsa@fdafd',
                 'phone_number': '43232423423',
                 'csrf_token': token}
    response = app.post('/new_user', auth_data, status='2*')
    assert b"Missing Required Fields" in response.body


def test_new_user_post_passwords_not_match(app_and_csrf_token, populated_db):
    '''Checks the POST form missing fields'''
    app, token = app_and_csrf_token
    auth_data = {'username': 'jkfdajkfda',
                 'password': 'fakefakefake',
                 'password_verify': 'fdsafda',
                 'last_name': 'Smith',
                 'first_name': 'Zeek',
                 'email': 'fdsa@fdafd',
                 'phone_number': '43232423423',
                 'csrf_token': token}
    response = app.post('/new_user', auth_data, status='2*')
    assert b'Passwords do not match or password'\
        b'is less then 6 characters' in response.body


def test_new_user_post_short_password(app_and_csrf_token, populated_db):
    '''Checks the POST form missing fields'''
    app, token = app_and_csrf_token
    auth_data = {'username': 'jkfdajkfda',
                 'password': 'fake',
                 'password_verify': 'fake',
                 'last_name': 'Smith',
                 'first_name': 'Zeek',
                 'email': 'fdsa@fdafd',
                 'phone_number': '43232423423',
                 'csrf_token': token}
    response = app.post('/new_user', auth_data, status='2*')
    assert b'Passwords do not match or password'\
        b'is less then 6 characters' in response.body


def test_new_user_post_user_name_exists(app_and_csrf_token, populated_db):
    '''Checks the POST form missing fields'''
    app, token = app_and_csrf_token
    auth_data = {'username': 'fake',
                 'password': 'fakefake',
                 'password_verify': 'fakefake',
                 'last_name': 'Smith',
                 'first_name': 'Zeek',
                 'email': 'fdsa@fdafd',
                 'phone_number': '43232423423',
                 'csrf_token': token}
    response = app.post('/new_user', auth_data, status='2*')
    assert b'already exists.' in response.body


def test_new_user_post_valid(app_and_csrf_token, populated_db):
    '''Checks the POST form missing fields'''
    app, token = app_and_csrf_token
    auth_data = {'username': 'fdsafdsafdsafsa',
                 'password': 'fakefake',
                 'password_verify': 'fakefake',
                 'last_name': 'Smith',
                 'first_name': 'Zeek',
                 'email': 'fdsa@fdafd',
                 'phone_number': '43232423423',
                 'csrf_token': token}
    response = app.post('/new_user', auth_data, status='3*')
    assert response.status_code == 302














# ffds
