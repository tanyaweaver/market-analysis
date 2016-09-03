"""Experimental API stuff.

Markit on demand.
http://dev.markitondemand.com/MODApis/
--> has search (LookUp), prices(Quote) with other data like change from 
yesterday, and graphs(InteractiveChart).
"""

import requests

def get_response_from_markit():
    resp = requests.get('http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input=AAP')
    if resp.status_code == 200:
        print('Content when searching for "AAP":')
        print(resp.content)
        print('Grabbing results to show it in a readable form...')
        for result in resp.json():
            print('{} {} {}'.format(result['Exchange'], result['Name'], result['Symbol']))

<<<<<<< HEAD
# example to use the search
print('Searching for AAP...')
resp = requests.get('http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input=AAP')
if resp.status_code == 200:
    print('Content when searching for "AAP":')
    print(resp.content)
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
    print('Grabbing results to show it in a readable form...')
    for key, value in resp.json().items():
        print('{} : {}'.format(key, value))
else:
    print('Error connecting to API')
    print(resp.status_code)
=======
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
        print('Grabbing results to show it in a readable form...')
        entries = {}
        for key, value in resp.json().items():
            entries[key] = value
        for key in entries:
            print(key + ':' , entries[key])
    else:
        print('Error connecting to API')
        print(resp.status_code)


if __name__ == '__main__':
    print('Searching for AAPL...')
    get_response_from_markit()
>>>>>>> staging
