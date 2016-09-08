from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from sqlalchemy.exc import DBAPIError
from sqlalchemy import and_, or_
try:
    from urllib.parse import urlencode
except ImportError:     # pragma: no cover
    from urllib import urlencode
from ..models import Stocks, Users, Association
from ..security import check_credentials
from passlib.apps import custom_app_context as pwd_context
import datetime
import requests


@view_config(route_name='search', renderer='../templates/search.jinja2',
                        permission='secret')
def search_stocks(request):
    msg = 'Search for stocks that you would like to watch.'
    search_results = []
    if request.method == 'GET':
        return {'stocks': search_results, 'msg': msg}
    elif request.method == 'POST':
        try:
            search = request.params.get('search')
            search1 = search.lower().capitalize()
            search2 = search.upper()
            search_query = request.dbsession.query(Stocks)\
                .filter(or_(Stocks.name.startswith(search1),
                        Stocks.symbol.startswith(search2)))
        except DBAPIError:  # pragma: no cover
            return Response(db_err_msg, content_type='text/plain', status=500)
        for row in search_query:
            search_results.append(row)
        if len(search_results) == 0:
            msg = 'No results found, try again.'
        return {'stocks': search_results, 'msg': msg}


@view_config(route_name='add', renderer='../templates/add_page.jinja2',
             permission='secret')
def add_stock_to_portfolio(request):
    if request.method == 'POST':
        current_user_id = request.dbsession.query(Users).filter(
                Users.username == request.authenticated_userid
            ).first().id
        new_stock_id = request.matchdict['id']
        query = request.dbsession.query(Association)\
            .filter(Association.user_id == current_user_id)
        list_of_stock_ids = []
        for row in query:
            list_of_stock_ids.append(row.stock_id)
        if int(new_stock_id) not in list_of_stock_ids:
            association_row = Association(user_id=current_user_id,
                                          stock_id=new_stock_id, shares=0)
            request.dbsession.add(association_row)
            msg = request.matchdict['name'] + ' was added to your portfolio.'
        else:
            msg = request.matchdict['name'] + ' is already in your portfolio.'
        return {'msg': msg}


@view_config(route_name='delete', renderer='../templates/delete_page.jinja2',
             permission='secret')
def delete_stock_from_portfolio(request):
    if request.method == 'POST':
        current_user_id = request.dbsession.query(Users).filter(
                Users.username == request.authenticated_userid
            ).first().id
        new_stock_sym = request.matchdict['sym']
        try:
            query = request.dbsession.query(Stocks).\
             filter(Stocks.symbol == new_stock_sym).first()
            query_del = request.dbsession.query(Association)\
                .filter(and_(Association.stock_id == query.id,
                             Association.user_id == current_user_id)).first()
            request.dbsession.delete(query_del)
            msg = request.matchdict['sym'] + ' was removed from'\
                ' your portfolio.'
        except AttributeError:
            msg = 'Failed: tried to remove a stock that is not in the'\
                ' portfolio.'
    else:
        msg = 'Failed: improper request.'
    return {'msg': msg}


@view_config(route_name='private',
             renderer='string',
             permission='secret')
def private(request):
    return "I'm a private view."


@view_config(route_name='public', renderer='string',
             permission='view')
def pubic(request):
    return "I'm a public page"


@view_config(route_name='portfolio', renderer="../templates/portfolio.jinja2",
             permission='secret')
def portfolio(request):
    """
    The main user portfolio page, displays a list of
    their stocks and a graph. Update number of shares.
    """
    current_user_id = request.dbsession.query(Users).filter(
                Users.username == request.authenticated_userid
            ).first().id
    query = request.dbsession.query(Users).\
        filter(Users.id == current_user_id).first()
    query = query.children

    if request.method == 'POST':
        updated_amount = request.POST['amount']
        for item, val in request.POST.items():
            if val == 'Update':
                updated_stock = item
        current_stock_id = request.dbsession.query(Stocks)\
            .filter(Stocks.symbol == updated_stock).first().id
        request.dbsession.query(Association)\
            .filter(and_(current_stock_id == Association.stock_id,
                    Association.user_id == current_user_id))\
            .update({Association.shares: updated_amount})

    list_of_stock_ids = []
    for row in query:
        list_of_stock_ids.append(row.child.symbol)
    if len(list_of_stock_ids) == 0:
        return HTTPFound(location=request.route_url('search'))
    else:
        elements = []
        for stock in list_of_stock_ids:
            elements.append({'Symbol': str(stock),
                             'Type': 'price', 'Params': ['c']})
        return build_graph(request, elements, True)


@view_config(route_name='details', renderer="../templates/details.jinja2",
                        permission="secret")
def single_stock_details(request):
    """Details for single-stock."""
    entries = {}
    elements = []
    msg = ''
    sym = request.matchdict['sym']
    resp = requests.get('http://dev.markitondemand.com/'
                        'Api/v2/Quote/json?symbol=' + sym)
    if resp.status_code == 200:
        entries = {key: value for key, value in resp.json().items()}
        if 'Message' in entries.keys():
            msg = 'Bad request.'
            entries = {}
        elements.append({'Symbol': str(sym), 'Type': 'price', 'Params': ['c']})
    else:
        entries = {}
        msg = 'Could not fulfill the request.'
    temp = build_graph(request, elements)
    try:
        temp['info'] = entries
        temp['msg'] = msg
    except TypeError:
        temp = {}
        temp['info'] = entries
        msg = 'Trouble connecting to API.'
        temp['msg'] = msg
    return temp


@view_config(route_name='admin', renderer="../templates/admin.jinja2",
             permission='admin')
def admin(request):
    '''A page to display a users information to the site adimn and allow
        them to change and update user information, or remove user'''
    message = ''
    if request.method == 'POST':
        username = request.POST['username']
        message = 'The delete button was pressed for user {}'.format(username)
    try:
        query = request.dbsession.query(Users)
        users = query.all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'users': users, 'message': message}


@view_config(route_name='home')
def home(request):
    if request.authenticated_userid:
        headers = remember(request, request.authenticated_userid)
        return HTTPFound(location=request.route_url('portfolio'),
                         headers=headers)
    else:
        return HTTPFound(location=request.route_url('login'))


@view_config(route_name='login', renderer='templates/login.jinja2')
def login(request):
    if request.method == 'POST':
        username = request.params.get('username', '')
        password = request.params.get('password', '')
        if check_credentials(request, username, password):
            headers = remember(request, username)
            try:
                query = request.dbsession.query(Users)
                user = query.filter_by(username=username).first()
                user.date_last_logged = datetime.datetime.now()
            except DBAPIError:  # pragma: no cover
                return Response(db_err_msg, content_type='text/plain',
                                status=500)
            return HTTPFound(location=request.route_url('portfolio'),
                             headers=headers)
        else:
            return {'error': "Username or Password Not Recognized"}
    return {'error': ''}


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('login'), headers=headers)


def format_dates(date_list):
    ret_list = []
    for date in date_list:
        date = date[5:10]
        ret_list.append(date)
    return ret_list


def convert_to_percentage(y_vals):
    """Convert a list of y_values to be percentage based first val."""
    initial = y_vals[0]
    ret_list = []
    for val in y_vals:
        val = round((val / initial - 1) * 100, 5)
        ret_list.append(val)
    return ret_list


def build_graph(request, elements, percentage=False):
# def build_graph(request, elements, msg):
    """Builds the graph from an API request."""

    url = 'http://dev.markitondemand.com/MODApis/Api/v2/InteractiveChart/json'
    req_obj = {
        "parameters":
        {
            'Normalized': 'false',
            'NumberOfDays': 14,
            'DataPeriod': 'Day',
            'Elements': elements
        }
    }

    total_shares = 0
    total_value = 0

    resp = requests.get(url, params=urlencode(req_obj))

    if resp.status_code == 200:
        entries = {}
        for key, value in resp.json().items():
            entries[key] = value
        print('entries:', entries)

        # build export dict for template
        export = {}
        export['dates'] = format_dates(entries['Dates'])
        export['x_values'] = entries['Positions']

        daily_totals = [0 for j in range(len(export['x_values']))]

        stocks = {}
        current_user_id = request.dbsession.query(Users).filter(
            Users.username == request.authenticated_userid
        ).first().id
        for series in entries['Elements']:
            current_stock_id = request.dbsession.query(Stocks)\
                .filter(Stocks.symbol == series['Symbol']).first().id
            shares = request.dbsession.query(Association).\
                filter(and_(Association.stock_id == current_stock_id,
                       Association.user_id == current_user_id)).first().shares

            y_vals = series['DataSeries']['close']['values']
            price = y_vals[-1]

            if not shares:
                shares = 0
            shares = int(shares)
            total_shares += (shares)
            total_value += (price) * (shares)

            for i in range(len(y_vals)):
                daily_totals[i] += (y_vals[i] * shares)
                print(daily_totals)

            if percentage:
                y_vals = convert_to_percentage(y_vals)

            stocks[series['Symbol']] = {
                'y_values': y_vals,
                'price': price,
                'max': series['DataSeries']['close']['max'],
                'min': series['DataSeries']['close']['min'],
                'shares': shares,
                'value': price * shares,
            }

        daily_change = []
        for tot in daily_totals:
            if daily_totals[0] > 0:
                daily_change\
                    .append(round(((tot * 100 / daily_totals[0]) - 100), 5))
            else:
                daily_change.append(0)

        if percentage:
            stocks['Total'] = {
                'y_values': daily_change,
                'price': round(total_value, 2),
                'shares': total_shares,
                'value': round(total_value, 2),
            }

        export['stocks'] = stocks
        export['total_shares'] = total_shares
        export['total_value'] = round((total_value), 2)

        print('export:', export)
        return {'entry': export}

    else:
        print('Error connecting to API')
        print(resp.status_code)
        return {'entry': {}}


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
            if username != '' and password != '' and password_verify != ''\
               and first_name != '' and last_name != '' and email != '':

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
                        is_admin=0,
                    )
                    request.dbsession.add(new)
                    headers = remember(request, username)
                    return HTTPFound(location=request.route_url('search'),
                                     headers=headers)
                else:
                    error = 'Passwords do not match or password'\
                            'is less then 6 characters'
            else:
                error = 'Missing Required Fields'

    return {'error': error, 'username': username, 'first_name': first_name,
            'last_name': last_name, 'phone_number': phone_number,
            'email': email, 'message': message}


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
