import os
from pyramid import testing
import pytest
import transaction
from .models import (
    get_engine,
    get_session_factory,
    get_tm_session
    )
from .models.mymodel import (
    Users,
    Stocks,
    Association
    )
from .models.meta import Base

def test_public_view(app):
    response = app.get('/login')
    assert response.status_code == 200


def test_init_db():
    pass
