import requests
import sys
from bs4 import BeautifulSoup
import re
# import geocoder
# import json

# https://finance.yahoo.com/q/?s=&bypass=true&ltr=1
# https://finance.yahoo.com/quote/AMZN?ltr=1
DOMAIN_NAME = 'http://dev.markitondemand.com/Api/v2/Quote/json?symbol=AAPL'
PATH = '/quote'
QUERY_PARAMS = {
    'Output': 'W',
    'Business_Name': '',
    'Business_Address': '',
    'Longitude': '',
    'Latitude': '',
    'City': '',
    'Zip_Code': '',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'H',
}


def get_inspection_page(**kwargs):
    """
    Make a request to the King County server.
    Fetch a set of search results. Takes query parameters as arguments.
    Return the bytes content of the response and encoding.
    Raise an error if there is a problem with the response.
    """
    url = DOMAIN_NAME + PATH
    params = QUERY_PARAMS.copy()
    for key, val in kwargs.items():
        if key in QUERY_PARAMS:
            params[key] = val
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.content, response.encoding


def load_inspection_page(path):
    """
    Read a static html (inspection_page.html).
    Return the bytes content and the encoding.
    Used for testing.
    """
    import io
    files = io.open(path, 'rb')
    response = files.read()
    files.close()
    encoding = 'utf-8'
    return response, encoding


def parse_source(html, encoding='utf-8'):
    """
    Parse the rsponse body using BeautifulSoup.
    Return the parsed object for further processing.
    """
    parsed = BeautifulSoup(html, 'html5lib', from_encoding=encoding)
    return parsed


# def extract_data_listings(html):
#     """
#     Takes in the parsed HTML. Return a list of the restaurant listing
#     container nodes.
#     """
#     id_finder = re.compile(r'PR[\d]+~')
#     return html.find_all('div', id=id_finder)


# def has_two_tds(element):
#     """
#     Takes an element as an argument.
#     Return 'True' if the element is both a <tr> and contains
#     two <td> elements within it, 'False' otherwise.
#     """
#     elem_is_tr = element.name == 'tr'
#     elem_has_td_children = element.find_all('td', recursive=False)
#     has_two_td = len(elem_has_td_children) == 2
#     return elem_is_tr and has_two_td


# def clean_data(element):
#     """
#     Takes a cell as an argument. Return the tag.string attribute
#     with extraneous characters stripped.
#     """
#     data = element.string
#     try:
#         return data.strip(" \n:-")
#     except AttributeError:
#         return u""


# def extract_restaurant_metadata(listing):
#     """
#     Take in the listing for a single restaurant.
#     Return a Python dict with metadata:
#     {<label>: <value>}.
#     """
#     listing_dict = {}
#     metadata_rows = listing.find('tbody').find_all(
#         has_two_tds, recursive=False
#     )
#     for row in metadata_rows:
#         for td in row.find_all('td', recursive=False):
#             key_row, val_row = row.find_all('td', recursive=False)
#             label_present = clean_data(key_row)
#             if label_present:
#                 label_dict = label_present
#             else:
#                 label_dict = ''
#             listing_dict.setdefault(label_dict, []).append(clean_data(val_row))
#     return listing_dict


# def is_inspection_row(element):
#     """A filter function. Take in an HTML element.
#     Return 'True' if the element matches the criteria:
#     1 - is a <tr> element,
#     2 - contains 4 <td> elements,
#     3 - word 'inspection' is in the text of it's first <td>,
#     4 - word 'inspection' is not the 1st word in that <td>.
#     Return 'False' otherwise.
#     """
#     is_tr = element.name == 'tr'
#     if not is_tr:
#         return False
#     td_children = element.find_all('td', recursive=False)
#     has_four_td = len(td_children) == 4
#     first_td_text = clean_data(td_children[0]).lower()
#     contains_word = 'inspection' in first_td_text
#     does_not_start = not first_td_text.startswith('inspection')
#     return is_tr and has_four_td and contains_word and does_not_start


# def extract_score_data(element):
#     """
#     Take a listing as an argument. Use a filter to find inspection rows.
#     Return a dict containing the average score, high score,
#     total inspection values.
#     """
#     inspection_rows = element.find_all(is_inspection_row)
#     samples = len(inspection_rows)
#     total = high_score = average = 0
#     for row in inspection_rows:
#         strval = clean_data(row.find_all('td')[2])
#         try:
#             intval = int(strval)
#         except (ValueError, TypeError):
#             samples -= 1
#         else:
#             total += intval
#             high_score = intval if intval > high_score else high_score
#     if samples:
#         average = total/float(samples)
#     data = {
#         u'Average Score': average,
#         u'High Score': high_score,
#         u'Total Inspections': samples
#     }
#     return data


# def generate_results(test=False, count=30):
#     """
#     Generate results using test settings or an API requst.
#     """
#     kwargs = {
#         'Inspection_Start': '1/1/2013',
#         'Inspection_End': '1/10/2013',
#         'City': 'Seattle',
#         'Zip_code': '98108'
#     }
#     if test:
#         html, encoding = load_inspection_page('src/inspection_page.html')
#     else:
#         html, encoding = get_inspection_page(**kwargs)
#     doc = parse_source(html, encoding)
#     listings = extract_data_listings(doc)
#     for listing in listings[:count]:
#         metadata = extract_restaurant_metadata(listing)
#         score_data = extract_score_data(listing)
#         metadata.update(score_data)
#         yield metadata


# def get_geojson(result):
#     """
#     Take the search result as an input. Get geocoding data from
#     google using the address of the restaurant. Build a dict
#     containing only particular values from the inspection record.
#     Replace properties of geojson with the dict values.
#     Return modified geojson record.
#     """
#     address = ' '.join(result.get('Address', ' '))
#     if not address:
#         return None
#     geocoded = geocoder.google(address)
#     geojson = geocoded.geojson
#     inspection_data = {}
#     use_keys = (
#         'Buisness Name', 'Average Score', 'Total Inspections', 'High Score',
#         'Address',
#         )
#     for key, val in result.items():
#         if key not in use_keys:
#             continue
#         if isinstance(val, list):
#             val = ' '.join(val)
#         inspection_data[key] = val
#     new_address  = geojson['properties'].get('address')
#     if new_address:
#         inspection_data['Address'] = new_address
#     geojson['properties'] = inspection_data
#     return geojson
#     return geocoded.geojson


# if __name__ == "__main__":
#     import pprint
#     test = len(sys.argv) > 1 and sys.argv[1] == 'test'
#     total_result = {'type': 'FeatureCollection', 'features': []}
#     for result in generate_results(test):
#         geo_result = get_geojson(result)
#         pprint.pprint(geo_result)
#         total_result['features'].append(geo_result)
#     with open('my_map.json', 'w') as fh:
#         json.dump(total_result, fh)

if __name__ == '__main__':
    # kwargs = {
    #     'Inspection_Start': '2/1/2013',
    #     'Inspection_End': '2/1/2015',
    #     'Zip_Code': '98109'
    # }
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # you will likely have something different here, depending on how
        # you implemented the load_inspection_page function.
        html, encoding = load_inspection_page('100nasdaq.html')
    # else:
    #     html, encoding = get_inspection_page(**kwargs)
    doc = parse_source(html, encoding)
    print (doc.prettify(encoding=encoding))
