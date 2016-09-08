
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
from sqlalchemy import and_

DATE = datetime.datetime.now()

def dummy_http_request(new_session, method='GET'):
    """Create the testing request and attach dbsession."""
    request = testing.DummyRequest()
    request.method = method
    request.dbsession = new_session
    return request


def test_user_model_gets_added(new_session, populated_db3):
    """Test that a new model gets added."""
    assert len(new_session.query(Users).all()) == 1
    model = Users(username='Jo', first_name='Jo', last_name='Reynolds', email='asdf@asdf.com', email_verified='True', date_joined=DATE, date_last_logged=DATE, pass_hash='asdfasdf', phone_number='555-555-5555', phone_number_verified='True', active='True', password_last_changed=DATE, password_expired='False')
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(Users).all()) == 2


def test_stock_model_gets_added(new_session, populated_db3):
    """Test that a new model gets added."""
    assert len(new_session.query(Stocks).all()) == 104
    model = Stocks(symbol='XYZ', name='zipper company', exchange='DOW')
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(Stocks).all()) == 105


def test_association_model_gets_added(new_session, populated_db3):
    """Test that a new model gets added."""
    assert len(new_session.query(Association).all()) == 5
    model = Association(user_id=1, stock_id=50, shares=20)
    new_session.add(model)
    new_session.flush()
    assert len(new_session.query(Association).all()) == 6


def test_portfolio_view_and_API_graph_data(new_session, populated_db3):
    """Test main portfolio page that entries is retrieved, and API
    works and graphs data is returned."""
    from .views.default import portfolio
    http_request = dummy_http_request(new_session)
    result = portfolio(http_request)
    assert len(result['entry']['stocks'].keys()) == 5


def test_search_stocks_letter(new_session, populated_db3):
    """Test the search functionality."""
    from .views.default import search_stocks
    http_request = dummy_http_request(new_session, 'POST')
    http_request.POST['search'] = 'a'
    result = search_stocks(http_request)
    assert len(result['stocks']) == 13


def test_search_stocks_name(new_session, populated_db3):
    """Test the search functionality."""
    from .views.default import search_stocks
    http_request = dummy_http_request(new_session, 'POST')
    http_request.POST['search'] = 'alphabet'
    result = search_stocks(http_request)
    assert result['stocks'][0].name == 'Alphabet Inc.' and len(result['stocks']) == 1


def test_search_stocks_error(new_session, populated_db3):
    """Test the search functionality."""
    from .views.default import search_stocks
    http_request = dummy_http_request(new_session, 'POST')
    http_request.POST['search'] = 'afdjfgdfd'
    result = search_stocks(http_request)
    assert result['msg'] == 'No results found, try again.'


def test_search_stocks_GET(new_session, populated_db3):
    """Test the search functionality."""
    from .views.default import search_stocks
    http_request = dummy_http_request(new_session, 'GET')
    http_request.POST['search'] = 'a'
    result = search_stocks(http_request)
    assert result == {'stocks': [], 'msg': 'Search for stocks that you'
                                    ' would like to watch.'}


def test_add_new_stock_to_portfolio_msg(new_session, populated_db3):
    from .views.default import add_stock_to_portfolio
    http_request = dummy_http_request(new_session, 'POST')
    http_request.matchdict['name'] = 'Baidu, Inc.'
    http_request.matchdict['id'] = 14
    result = add_stock_to_portfolio(http_request)
    assert result['msg'] == 'Baidu, Inc. was added to your portfolio.'


def test_add_existing_stock_to_portfolio_msg(new_session, populated_db3):
        from .views.default import add_stock_to_portfolio
        http_request = dummy_http_request(new_session, 'POST')
        http_request.matchdict['name'] = 'Activision Blizzard, Inc.'
        http_request.matchdict['id'] = 1
        result = add_stock_to_portfolio(http_request)
        assert result['msg'] == 'Activision Blizzard, Inc. is '\
            'already in your portfolio.'


def test_add_new_stock_to_portfolio_db(new_session, populated_db3):
    from .views.default import add_stock_to_portfolio
    http_request = dummy_http_request(new_session, 'POST')
    http_request.matchdict['name'] = 'Baidu, Inc.'
    http_request.matchdict['id'] = 14
    add_stock_to_portfolio(http_request)
    user_id = 1
    query = http_request.dbsession.query(Association).\
        filter(Association.user_id == user_id).all()
    assert len(query) == 6


def test_add_existing_stock_to_portfolio_db(new_session, populated_db3):
        from .views.default import add_stock_to_portfolio
        http_request = dummy_http_request(new_session, 'POST')
        http_request.matchdict['name'] = 'Activision Blizzard, Inc.'
        http_request.matchdict['id'] = 1
        add_stock_to_portfolio(http_request)
        user_id = 1
        query = http_request.dbsession.query(Association).\
            filter(Association.user_id == user_id).all()
        assert len(query) == 5


def test_add_new_stock_to_portfolio_stock_id(new_session, populated_db3):
    from .views.default import add_stock_to_portfolio
    http_request = dummy_http_request(new_session, 'POST')
    http_request.matchdict['name'] = 'Baidu, Inc.'
    http_request.matchdict['id'] = 14
    add_stock_to_portfolio(http_request)
    user_id = 1
    query = http_request.dbsession.query(Association).\
        filter(Association.user_id == user_id)
    list_of_stock_ids = []
    for row in query:
        list_of_stock_ids.append(row.stock_id)
    assert 14 in list_of_stock_ids


def test_add_existing_stock_to_portfolio_stock_id(new_session, populated_db3):
        from .views.default import add_stock_to_portfolio
        http_request = dummy_http_request(new_session, 'POST')
        http_request.matchdict['name'] = 'Activision Blizzard, Inc.'
        http_request.matchdict['id'] = 1
        add_stock_to_portfolio(http_request)
        user_id = 1
        query = http_request.dbsession.query(Association).\
            filter(Association.user_id == user_id)
        list_of_stock_ids = []
        for row in query:
            list_of_stock_ids.append(row.stock_id)
        assert 1 in list_of_stock_ids


# # Test del_stock_from_portfolio()


def test_del_stock_from_portfolio_msg(new_session, populated_db3):
        from .views.default import delete_stock_from_portfolio
        user_id = 1
        http_request = dummy_http_request(new_session, 'POST')
        http_request.matchdict['sym'] = 'ATVI'
        result = delete_stock_from_portfolio(http_request)
        assert result['msg'] == 'ATVI was removed from your portfolio.'


def test_del_stock_from_portfolio_db(new_session, populated_db3):
    from .views.default import delete_stock_from_portfolio
    user_id = 1 
    http_request = dummy_http_request(new_session, 'POST')
    http_request.matchdict['sym'] = 'ATVI'
    delete_stock_from_portfolio(http_request)
    query = http_request.dbsession.query(Association).\
        filter(Association.user_id == user_id).all()
    assert len(query) == 4


def test_del_stock_from_portfolio_stock_id(new_session, populated_db3):
    from .views.default import delete_stock_from_portfolio
    user_id = 1
    http_request = dummy_http_request(new_session, 'POST')
    http_request.matchdict['sym'] = 'ATVI'
    delete_stock_from_portfolio(http_request)
    query = http_request.dbsession.query(Association)\
        .filter(Association.user_id == user_id)
    list_of_stock_ids = []
    for row in query:
        list_of_stock_ids.append(row.stock_id)
    assert 1 not in list_of_stock_ids


def test_del_stock_from_portfolio_error_POST(new_session, populated_db3):
    from .views.default import delete_stock_from_portfolio
    user_id = 1
    http_request = dummy_http_request(new_session, 'POST')
    http_request.matchdict['sym'] = 'ATVIVV'
    result = delete_stock_from_portfolio(http_request)
    assert result['msg'] == 'Failed: tried to remove a stock that is not'\
        ' in the portfolio.'


def test_del_stock_from_portfolio_error_GET(new_session, populated_db3):
    from .views.default import delete_stock_from_portfolio
    user_id = 1
    http_request = dummy_http_request(new_session, 'GET')
    http_request.matchdict['sym'] = 'ATVI'
    result = delete_stock_from_portfolio(http_request)
    assert result['msg'] == 'Failed: improper request.'


def test_details_ok(new_session, populated_db3):
    from .views.default import single_stock_details
    http_request = dummy_http_request(new_session)
    http_request.matchdict['sym'] = 'ATVI'
    result = single_stock_details(http_request)
    assert result['info']['Symbol'] == 'ATVI'


def test_update_shares(new_session, populated_db3):
        from .views.default import portfolio
        http_request = dummy_http_request(new_session, 'POST')
        http_request.POST['amount'] = 9
        http_request.POST['ATVI'] = 'Update'
        user_id = 1
        query_before = http_request.dbsession.query(Association).\
            filter(and_(Association.user_id == user_id, Association.stock_id == 1)).first().shares
        assert query_before == 10
        portfolio(http_request)
        query_after = http_request.dbsession.query(Association).\
            filter(and_(Association.user_id == user_id, Association.stock_id == 1)).first().shares
        assert query_after == 9


# def test_details_error_sym(app, new_session):
#     from .views.default import single_stock_details
#     http_request = dummy_http_request(new_session)
#     http_request.matchdict['sym'] = 'CSCODSR'
#     result = single_stock_details(http_request)
#     assert result == {'info': {}, 'msg': 'Bad request.'}


# May return to this later
# def test_details_error_resp_status(new_session):
#     from .views.default import single_stock_details
#     http_request = dummy_http_request(new_session)
#     http_request.matchdict['sym'] = 'CSCO'
#     result = single_stock_details(http_request)
#     result.status_code = 404
#     assert result == {'entry': {}, 'msg': 'Could not fulfill the request.'}
