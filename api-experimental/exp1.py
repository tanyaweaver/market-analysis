"""Experimental API stuff.

Markit on demand.
http://dev.markitondemand.com/MODApis/
--> has search (LookUp), prices(Quote) with other data like change from
yesterday, and graphs(InteractiveChart).
"""

import requests
from urllib.parse import urlencode


def get_response_from_markit():

    # example to use Lookup
    print('Searching for AAPL...')
    resp = requests.get('http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input=AAP')
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
            'NumberOfDays': 5,
            'DataPeriod': 'Day',
            'Elements': elements
        }
    }

    resp = requests.get(url, params=urlencode(req_obj))

    print('Getting chart data for Apple and Google...')
    print('')

    if resp.status_code == 200:
        print('Content when getting chart info for AAPL and GOOGL:')
        print(resp.content)
        print('')
        print('Grabbing results to show it in a readable form...')
        entries = {}
        for key, value in resp.json().items():
            entries[key] = value

        print('')
        print('Here is the entries dict returned:')
        print(entries)

        # package data up for easy graph implementation
        export = {}
        export['dates'] = entries['Dates']
        export['x_values'] = entries['Positions']

        print('')
        print('series:')
        stocks = {}
        for series in entries['Elements']:
            print(series)
            stocks[series['Symbol']] = {
                'y_values': series['DataSeries']['close']['values'],
                'currency': series['Currency'],
                'max': series['DataSeries']['close']['max'],
                'min': series['DataSeries']['close']['min'],

            }

        export['stocks'] = stocks
        print('')
        print('export dict:')
        print(export)

        # build graph
        import matplotlib.pyplot as plt, mpld3
        plot = plt.plot([3, 1, 4, 1, 5], 'ks-', mec='w', mew=5, ms=20)
        mpld3.fig_to_html(plot)

    else:
        print('Error connecting to API')
        print(resp.status_code)


if __name__ == '__main__':
    get_response_from_markit()
