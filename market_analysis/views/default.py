from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError

# from ..models import MyModel
from urllib.parse import urlencode
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from ..models import Users
from ..security import check_credentials
from passlib.apps import custom_app_context as pwd_context

import datetime
import requests

STOCKS = [
    {'id': 1, 'symbol': 'MSFT', 'value': 123.55},
    {'id': 2, 'symbol': 'AMZN', 'value': 745.27},
]


@view_config(route_name='private',
             renderer='string',
             permission='secret')
def private(request):
    return "I'm a private view."


@view_config(route_name='public', renderer='string',
             permission='view')
def pubic(request):
    return "I'm a public page"


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
    try:
        query = request.dbsession.query(Users)
        users = query.all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'users': users, 'messages': {}}


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('search'), headers=headers)


# TODO: if there is a login failure give a message, and stay here
@view_config(route_name='login', renderer='templates/login.jinja2')
def login(request):
    if request.method == 'POST':
        # import pdb; pdb.set_trace()

        username = request.params.get('username', '')
        password = request.params.get('password', '')
        # import pdb; pdb.set_trace()
        if check_credentials(request, username, password):
            headers = remember(request, username)
            try:
                query = request.dbsession.query(Users)
                user = query.filter_by(username=username).first()
                user.date_last_logged = datetime.datetime.now()
            except DBAPIError:
                return Response(db_err_msg, content_type='text/plain', status=500)
            return HTTPFound(location=request.route_url('portfolio'),
                             headers=headers)
        else:
            return {'error': "Username or Password Not Recognized"}
    return {'error': ''}


@view_config(route_name='new_user', renderer='templates/new_user.jinja2')
def new_user(request):
    username = password = password_verify = first_name = ''
    last_name = phone_number = email = error = message = ''

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_verify = request.POST['password_verify']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone_number = request.POST['phone_number']
        email = request.POST['email']

        try:
            query = request.dbsession.query(Users)
            result = query.filter_by(username=username).first()
        except DBAPIError:
            return Response(db_err_msg, content_type='text/plain', status=500)

        if result:
            message = 'User "{}" already exists.'.format(username)
        else:
            if username != '' and password != '' and password_verify != '' and \
               first_name != '' and last_name != '' and email != '':

                if (password == password_verify) and (len(password) > 6):
                    message = "good job, you can enter info"
                    date_joined = datetime.datetime.now()
                    date_last_logged = datetime.datetime.now()
                    new = Users(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        email_verified=0,
                        date_joined=date_joined,
                        date_last_logged=date_last_logged,
                        pass_hash=pwd_context.encrypt(password),
                        phone_number=phone_number,
                        phone_number_verified=0,
                        active=1,
                        password_last_changed=datetime.datetime.now(),
                        password_expired=1,
                    )
                    request.dbsession.add(new)
                    return HTTPFound(location=request.route_url('admin'))
                else:
                    error = 'Passwords do not match or password \
                             is less then 6 characters'
            else:
                error = 'Missing Required Fields'

    return {'error': error, 'username': username, 'first_name': first_name,
            'last_name': last_name, 'phone_number': phone_number,
            'email': email, 'message': message}


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
