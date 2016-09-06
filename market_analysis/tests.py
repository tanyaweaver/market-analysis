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
import datetime
from sqlalchemy.orm import relationship

def test_public_view(app):
    response = app.get('/login')
    assert response.status_code == 200


def test_init_db():
    pass


@pytest.fixture(scope="session")
def sqlengine(request):
    config = testing.setUp(settings={
        'sqlalchemy.url': 'sqlite:///:memory:'
    })
    config.include(".models")
    settings = config.get_settings()
    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    def teardown():
        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return engine


@pytest.fixture(scope="function")
def new_session(sqlengine, request):
    session_factory = get_session_factory(sqlengine)
    session = get_tm_session(session_factory, transaction.manager)

    def teardown():
        transaction.abort()

    request.addfinalizer(teardown)
    return session


date = datetime.datetime.now()


def test_user_model_gets_added(new_session):
    """Test that a new model gets added."""
    assert len(new_session.query(Users).all()) == 0
    model = Users(username='Tom', first_name='Tom', last_name='Reynolds', email='asdf@asdf.com', email_verified=True, date_joined=date, date_last_logged=date, pass_hash='asdfasdf', phone_number='555-555-5555', phone_number_verified=True, active=True, password_last_changed=date, password_expired=False)
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(Users).all()) == 1


def test_stock_model_gets_added(new_session):
    """Test that a new model gets added."""
    assert len(new_session.query(Stocks).all()) == 0
    model = Stocks(symbol='XYZ', name='zipper company', exchange='DOW')
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(Stocks).all()) == 1


def test_association_model_gets_added(new_session):
    """Test that a new model gets added."""
    assert len(new_session.query(Association).all()) == 0
    model = Association(user_id=500, stock_id=500, shares=20)
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(Association).all()) == 1


def dummy_http_request(new_session, method='GET'):
    """Create the testing request and attach dbsession."""
    request = testing.DummyRequest()
    request.method = method
    request.dbsession = new_session
    return request


#def test_portfolio_view_and_API_graph_data(new_session):
#    """Test main portfolio page that entries is retrieved, and API

#    works and graphs data is returned."""
#    from .views.default import portfolio

#    model = Stocks(symbol='GOOGL', name='zipper company', exchange='DOW')
#    new_session.add(model)
#    model = Stocks(symbol='AMZN', name='zipper company2', exchange='DOW')
#    new_session.add(model)
#    new_session.flush()

#    model = Association(user_id=1, stock_id=1, shares=20)
#    new_session.add(model)
#    model = Association(user_id=1, stock_id=2, shares=20)
#    new_session.add(model)
#    new_session.flush()

#    model = Users(username='Tom', first_name='Tom', last_name='Reynolds', email='asdf@asdf.com', email_verified=True, date_joined=date, date_last_logged=date, pass_hash='asdfasdf', phone_number='555-555-5555', phone_number_verified=True, active=True, password_last_changed=date, password_expired=False)
#    new_session.add(model)
#    new_session.flush()

#    http_request = dummy_http_request(new_session)
#    result = portfolio(http_request)
#    assert len(result['entry']['stocks'].keys()) == 2


def test_search_letter(new_session):
    """Test the search functionality."""
    from .views.default import search
    from market_analysis.scripts.test_db import STOCKS_100
    for line in STOCKS_100:
        model = Stocks(symbol=line[0], name=line[1], exchange='NASDAQ')
        new_session.add(model)
    new_session.flush()

    http_request = dummy_http_request(new_session, 'POST')
    http_request.POST['search'] = 'a'
    result = search(http_request)
    assert len(result['stocks']) == 13


def test_search_name(new_session):
    """Test the search functionality."""
    from .views.default import search
    from market_analysis.scripts.test_db import STOCKS_100
    for line in STOCKS_100:
        model = Stocks(symbol=line[0], name=line[1], exchange='NASDAQ')
        new_session.add(model)
    new_session.flush()

    http_request = dummy_http_request(new_session, 'POST')
    http_request.POST['search'] = 'alphabet'
    result = search(http_request)
    assert result['stocks'][0].name == 'Alphabet Inc.' and len(result['stocks']) == 1


#def test_new_get(new_session):
#    """Test new entry get req."""
#    from .views.default import new

#    new_session.add(MyModel(title="test", body='blah..', creation_date='1066 AD'))
#    new_session.flush()

#    http_request = dummy_http_request(new_session)
#    result = new(http_request)
#    assert result['entry']['goofed'] == 0


#def test_new_submit_fail(new_session):
#    """Test new entry fails when data incomplete."""
#    from .views.default import new

#    new_session.add(MyModel(title='', body='this should fail', creation_date=''))
#    new_session.flush()

#    http_request = dummy_http_request(new_session, 'POST')
#    http_request.POST['title'] = ''
#    http_request.POST['body'] = 'this should fail'
#    http_request.POST['creation_date'] = ''
#    result = new(http_request)
#    assert result['entry']['goofed'] == 1


#def test_detail(new_session):
#    """Test the correct entry is retrieved in detail view."""
#    from .views.default import detail

#    new_session.add(MyModel(title="test", body='blah..', creation_date='1066 AD'))
#    new_session.flush()

#    http_request = dummy_http_request(new_session)
#    http_request.matchdict['id'] = 1
#    result = detail(http_request)
#    assert getattr(result['entry'], 'title') == 'test'


#def test_edit(new_session):
#    """Test the editing page."""
#    from .views.default import edit

#    new_session.add(MyModel(title="test", body='blah..', creation_date='1066 AD'))
#    new_session.flush()

#    http_request = dummy_http_request(new_session, 'POST')
#    http_request.matchdict['id'] = 1
#    http_request.POST['title'] = 'new title'
#    http_request.POST['body'] = 'blah 2.0'
#    http_request.POST['creation_date'] = '1066 AD'
#    result = edit(http_request)
#    assert result['updated'] == True
