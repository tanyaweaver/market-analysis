import os
from pyramid import testing


def test_public_view(app):
    response = app.get('/login', status='2*')
    assert response.status_code == 200


def test_private_view(app):
    response = app.get('/private', status='4*')
    assert response.status_code == 403
