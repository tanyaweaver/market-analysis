"""Experimental API stuff.

Markit on demand.
http://dev.markitondemand.com/MODApis/
--> has search (LookUp), prices(Quote) with other data like change from
yesterday, and graphs(InteractiveChart).
"""
#from __future__ import unicode_literals
import requests
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


def get_response_from_markit():

    # example to use Lookup
    print('Searching for AAPL...')
    resp = requests.get('http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input=B')
    if resp.status_code == 200:
        print('Content when searching for "AAP":')
        print(resp.content)
        print('')
        print('Grabbing results to show it in a readable form...')
        for result in resp.json():
            print('{} {} {}'.format(result['Exchange'], result['Name'], result['Symbol']))
    else:
        print('Error connecting to API')
        print(resp.status_code)

    print('')
    print('-=' * 30)
    print('')

    # example to use Quote
    print('Getting quote info for AAPL')
    resp = requests.get('http://dev.markitondemand.com/Api/v2/Quote/json?symbol=AAPL')
    if resp.status_code == 200:
        print('Content when getting a quote for AAPL:')
        print(resp.content)
        print('')
        print('Grabbing results to show it in a readable form...')
        entries = {}
        for key, value in resp.json().items():
            entries[key] = value
        for key in entries:
            print(key + ':', entries[key])
    else:
        print('Error connecting to API')
        print(resp.status_code)

    print('')
    print('-=' * 30)
    print('')

    # example chart, using Google and Apple for 5 days, closing price
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
        print(entries)

        # build export dict for template
        export = {}
        export['x_values'] = entries[u'Positions']
        export['dates'] = entries[u'Dates']

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


if __name__ == '__main__':
    get_response_from_markit()
