from .models import Users
from .conftest import USER_CREDENTIALS
import pytest

PRIVATE_ROUTES = [
    ('/search'),
    ('/add/{name}/{id}'),
    ('/delete/{sym}'),
    ('/portfolio'),
    ('/details/{sym}'),
]

PUBLIC_ROUTES = [
    ('/login'),
    ('/about'),
    ('/new_user')
]


@pytest.mark.parametrize('route', PUBLIC_ROUTES)
def test_login_view_is_public(route, app):
    '''Test that unathurized user can access public routes.'''
    response = app.get(route, status='2*')
    assert response.status_code == 200


@pytest.mark.parametrize('route', PRIVATE_ROUTES)
def test_no_access_to_private_views_if_no_auth(route, app):
    """Test that unathurized user can't access private routes."""
    response = app.get(route, status='4*')
    assert response.status_code == 403


def test_user_db_exists(new_session):
    '''Tests that the use database is being setup'''
    assert len(new_session.query(Users).all()) == 0


def test_user_gets_added_to_db(new_session):
    '''Tests that a use can be added to the database'''
    user = Users(username=USER_CREDENTIALS['username'], pass_hash='hashiehas')
    new_session.add(user)
    new_session.flush()
    assert len(new_session.query(Users).all()) == 1


def test_login_correct_user_info(app_and_csrf_token, populated_db):
    '''Checks the POST form submital for correct user login data'''
    app, token = app_and_csrf_token
    auth_data = {'username': 'fake',
                 'password': 'fake',
                 'csrf_token': token}
    response = app.post('/login', auth_data, status='3*')
    assert response.status_code == 302


def test_login_bad_user_info(app_and_csrf_token, populated_db):
    '''Checks the POST form submital for correct user login data'''
    app, token = app_and_csrf_token
    auth_data = {'username': 'fake',
                 'password': 'not the correct password',
                 'csrf_token': token}
    response = app.post('/login', auth_data, status='2*')
    assert b"Username or Password Not Recognized" in response.body


def test_logout(app):
    '''Tests that the logout page re-routes the user'''
    response = app.get('/logout', status="3*")
    assert response.status_code == 302


def test_home_public(app):
    '''Test that the home view is publicly accessable'''
    response = app.get('/', status="3*")
    assert response.status_code == 302


def test_home_rederects_to_portfolio(auth_app, populated_db):
    '''Tests that the "/" route re-routes the user'''
    response = auth_app.get('/', status='3*')
    assert response.status_code == 302


def test_admin_is_private(app):
    '''Test that the admin page is not accessable if you are not logged in'''
    response = app.get('/admin', status='4*')
    assert response.status_code == 403


def test_admin_accessable_to_adim(admin_app, populated_db_admin):
    '''Testing the admin view is accessable to admin users'''
    app, token = admin_app
    response = app.get('/admin', status='2*')
    assert response.status_code == 200


def test_admin_not_accessable_to_non_admin(auth_app, populated_db):
    '''Testing that the admin view is not accessable to non-admin'''
    response = auth_app.get('/admin', status='4*')
    assert response.status_code == 403


def test_admin_delet_post_request_csrf(admin_app, populated_db):
    '''Checks admin view POST for correct CSRF Token'''
    app, token = admin_app
    auth_data = {'username': 'fake',
                 'csrf_token': token}
    response = app.post('/admin', auth_data, status='2*')
    assert response.status_code == 200


def test_new_user_is_public(app):
    '''Checking that the new_user view is public'''
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
        b' is less than 6 characters' in response.body


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
        b' is less than 6 characters' in response.body


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


def test_admin_delete_user_returns_message(admin_app, populated_db):
    '''
    Checks admin view DELETE button POST returns to admin with
    conformation method
    '''
    app, token = admin_app
    auth_data = {'username': 'fake',
                 'csrf_token': token}
    response = app.post('/admin', auth_data, status='2*')
    assert b'Are you sure you want to delete user fake?' in response.body


def test_admin_cancel_delete_user_returns_message(admin_app, populated_db):
    '''
    Checks admin view CANCEL button POST returns to admin without
    conformation method
    '''
    app, token = admin_app
    auth_data = {'username': 'CANCEL',
                 'csrf_token': token}
    response = app.post('/admin', auth_data, status='2*')
    assert b'Are you sure you want to delete user?' not in response.body
