from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

#from ..models import MyModel
from urllib.parse import urlencode
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from ..models import Users

import requests

STOCKS = [
    {'id': 1, 'symbol': 'MSFT', 'value': 123.55},
    {'id': 2, 'symbol': 'AMZN', 'value': 745.27},
]


@view_config(route_name='home_test',
             renderer='../templates/home_page_test.jinja2')
def home_test(request):
    return {}


@view_config(route_name='portfolio', renderer="../templates/portfolio.jinja2")
def portfolio(request):
    '''The main user portfolio page, displays a list of their stocks and other
       cool stuff'''
    return {'stocks': STOCKS}


@view_config(route_name='search', renderer="../templates/search.jinja2")
def search(request):
    '''A Search page that allows a user to search for a stock
        and provide a way to add stock to there portfolio'''
    return {'message': 'Search page'}


@view_config(route_name='userinfo', renderer="../templates/userinfo.jinja2")
def userinfo(request):
    '''A page to display a users information to the user and allow them to
        change and update it, or removethemselves from the list of users'''
    return {'message': 'User info page'}


@view_config(route_name='admin', renderer="../templates/admin.jinja2")
def admin(request):
    '''A page to display a users information to the site adimn and allow
        them to change and update user information, or remove user'''
    return {'message': 'Adimin Info Page'}



@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('search'), headers=headers)


# TODO: if there is a login failure give a message, and stay here
@view_config(route_name='login', renderer='templates/login.jinja2')
def login(request):
    # if request.method == 'POST':
    #     username = request.params.get('username', '')
    #     password = request.params.get('password', '')
    #     if check_credentials(username, password):
    #         headers = remember(request, username)
    #         return HTTPFound(location=request.route_url('home'),
    #                          headers=headers)
    #     else:
    #         return {'error': "Username or Password Not Recognized"}
    return {'error': ''}


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

@view_config(route_name='graph_demo', renderer='../templates/graphs.jinja2')
def graph_demo(request):
    url = 'http://dev.markitondemand.com/MODApis/Api/v2/InteractiveChart/json'
    elements = [
        {
            'Symbol': 'GOOGL',
            'Type': 'price',
            'Params': ['c'],
        },
        {
            'Symbol': 'AAPL',
            'Type': 'price',
            'Params': ['c'],
        }
    ]
    req_obj = {
        "parameters":
        {
            'Normalized': 'false',
            'NumberOfDays': 7,
            'DataPeriod': 'Day',
            'Elements': elements
        }
    }

    resp = requests.get(url, params=urlencode(req_obj))

    if resp.status_code == 200:
        entries = {}
        for key, value in resp.json().items():
            entries[key] = value

        # build export dict for template
        export = {}
        export['dates'] = entries['Dates']
        export['x_values'] = entries['Positions']

        stocks = {}
        for series in entries['Elements']:
            stocks[series['Symbol']] = {
                'y_values': series['DataSeries']['close']['values'],
                'currency': series['Currency'],
                'max': series['DataSeries']['close']['max'],
                'min': series['DataSeries']['close']['min'],

            }
        export['stocks'] = stocks
        print(export)
        return {'entry': export}

    else:
        print('Error connecting to API')
        print(resp.status_code)


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
