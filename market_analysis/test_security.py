# import os
from pyramid import testing


def test_public_view(app):
    response = app.get('/public', status='2*')
    assert response.status_code == 200


def test_private_view(app):
    response = app.get('/private', status='4*')
    assert response.status_code == 403

def test_private_view_accessable_to_authenticated(authenticated_app):
    response = authenticated_app.get('private', status='2*')
    assert response.status_code == 200
