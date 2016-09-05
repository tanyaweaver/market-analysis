from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import Stocks

import requests


@view_config(route_name='home_test', renderer='../templates/home_page_test.jinja2')
def home_test(request):
    return {}


@view_config(route_name='single_stock_info_test', renderer='../templates/single_stock_info_test.jinja2')
def single_stock_info_test(request):
    resp = requests.get('http://dev.markitondemand.com/Api/v2/Quote/json?symbol=AAPL')
    if resp.status_code == 200:
        entry = {}
        for key, value in resp.json().items():
            entry[key] = value
    else:
        print('Error connecting to API')
        print(resp.status_code)
    return {'entry': entry}


@view_config(route_name='search_test', renderer='../templates/search_page_test.jinja2')
def search_test(request):
    msg = 'Hi!'
    try:
        query = request.dbsession.query(Stocks)
        stocks = query.all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    if request.method == 'GET':
        return {'stocks': stocks[:10], 'msg': msg}
    elif request.method == 'POST':
        search_results = []
        for stock in stocks:
            search_name = request.params.get('search')
            search_query = request.dbsession.query(Stocks)\
                .filter(Stocks.name.startswith(search_name.lower().capitalize()))
        for row in search_query:
            search_results.append(row)
        if len(search_results) == 0:
            msg = 'No results found, try again.'
        return {'stocks': search_results, 'msg': msg}


@view_config(route_name='add_test', renderer='../templates/search_page_test.jinja2')
def add_test(request):
    msg = 'The stock was added to your portfolio.'
    return {'msg': msg}
db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_market-analysis_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
