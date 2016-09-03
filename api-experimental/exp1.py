"""Experimental API stuff.

Markit on demand.
http://dev.markitondemand.com/MODApis/
--> has search (LookUp), prices(Quote) with other data like change from 
yesterday, and graphs(InteractiveChart).
"""

import requests


# example to use the search
print('Searching for AAPL...')
resp = requests.get('http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input=AAPL')
if resp.status_code == 200:
    print('Content when searching for apple:')
    print(resp.content)
else:
    print('Error connecting to API')
    print(resp.status_code)

# example to use Quote
print('Getting quote info for AAPL')
resp = requests.get('http://dev.markitondemand.com/Api/v2/Quote/json?symbol=AAPL')
if resp.status_code == 200:
    print('Content when getting a quote for AAPL:')
    print(resp.content)
else:
    print('Error connecting to API')
    print(resp.status_code)
