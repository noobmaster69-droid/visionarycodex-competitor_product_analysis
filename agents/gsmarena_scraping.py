import logging

from bs4 import BeautifulSoup
import requests

# Sample HTML (you can replace this with the actual fetched HTML)
def scrape_data_from_gsmarena(query):
    link = scrape_for_gsmarena_link(query)
    response = requests.get("https://api.scrapingdog.com/scrape", params={
        'api_key': '67e19fc7eccb45caac0ab4bb',
        'url': url,
        'dynamic': 'false',
    })

    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    # Find the table containing "Platform" (Chipset, CPU, GPU, etc.)

    comms_table = None
    features_table = None
    body_table = None
    battery_table = None
    display_table = None
    platform_table = None
    for table in soup.find_all('table'):
        if table.find('th', text='Platform'):
            platform_table = table
        if table.find('th', text='Comms'):
            comms_table = table
        if table.find('th', text='Features'):
            features_table = table
        if table.find('th', text='Body'):
            body_table = table
        if table.find('th', text='Battery'):
            battery_table = table
        if table.find('th', text='Display'):
            display_table = table

    chip = ''
    display = ''
    battery = ''
    waterResistance = ''
    wirelessCharging = ''
    security = ''
    bluetooth = ''
    wifi = ''
    gps = ''
    nfc = ''
    dualSim = ''
    assistant = ''
    batteryLife = ''
    weight = ''
    thumbnail = ''
    protection = ''


    platform = {}
    if platform_table:
        rows = platform_table.find_all('tr')
        for row in rows[0:]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                platform[key] = value
    else:
        logging.info("Platform table not found.")

    comms = {}
    if comms_table:
        rows = comms_table.find_all('tr')
        for row in rows[0:]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                comms[key] = value
    else:
        logging.info("Comms table not found.")

    body = {}
    if body_table:
        rows = body_table.find_all('tr')

        for row in rows[0:]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                body[key] = value
    else:
        logging.info("Body table not found.")

    features = {}
    if features_table:
        rows = features_table.find_all('tr')

        for row in rows[0:]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                features[key] = value
    else:
        logging.info("features table not found.")

    display = {}
    if display_table:
        rows = display_table.find_all('tr')
        for row in rows[0:]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                display[key] = value
    else:
        logging.info("display table not found.")

    battery ={}
    if battery_table:
        rows = battery_table.find_all('tr')

        for row in rows[0:]:
            cells = row.find_all('td')
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                battery[key] = value
    else:
        logging.info("battery table not found.")

    if 'OS' in platform and 'iOS' in platform['OS']:
        assistant = 'Siri'
    else:
        assistant = 'Google Assistant'

    if 'SIM' in body and '+' in body['SIM']:
        dualSim = True
    else:
        dualSim = False

    if '' in body and 'water' in body['']:
        waterResistance = True
    else:
        waterResistance = False

    if 'Charging' in battery and 'wireless' in battery['Charging']:
        wirelessCharging = True
    else:
        wirelessCharging = False

    if 'Bluetooth' in comms and comms['Bluetooth'] is not None:
        bluetooth = True
    else:
        bluetooth = False

    if 'WLAN' in comms and comms['WLAN'] is not None:
        wifi = True
    else:
        wifi = False

    if 'Positioning' in comms and 'GPS' in comms['Positioning']:
        gps = True
    else:
        gps = False

    if 'NFC' in comms and comms['NFC'] is not None:
        nfc = True
    else:
        nfc = False
    features = {
        "chip": platform['Chipset'],
        "display": display['Resolution'],
        "battery": battery['Type'],
        "waterResistance": waterResistance,
        "wirelessCharging": wirelessCharging,
        "security": features['Sensors'].split()[0],
        "bluetooth": bluetooth,
        "wifi": wifi,
        "gps": gps,
        "nfc": nfc,
        "dualSim": dualSim,
        "assistant": assistant,
        "weight": body['Weight'],
        "protection": display['Protection']
    }
    return features

# def scrape_data_from_gsmarena(html):
#     soup = BeautifulSoup(html, 'html.parser')
#
#     # Find the tables
#     comms_table = None
#     features_table = None
#     body_table = None
#     battery_table = None
#     display_table = None
#     platform_table = None
#
#     for table in soup.find_all('table'):
#         if table.find('th', text='Platform'):
#             platform_table = table
#         if table.find('th', text='Comms'):
#             comms_table = table
#         if table.find('th', text='Features'):
#             features_table = table
#         if table.find('th', text='Body'):
#             body_table = table
#         if table.find('th', text='Battery'):
#             battery_table = table
#         if table.find('th', text='Display'):
#             display_table = table
#
#     # Function to extract data from a table
#     def extract_table_data(table):
#         data = {}
#         if table:
#             rows = table.find_all('tr')
#             for row in rows:
#                 cells = row.find_all('td')
#                 if len(cells) == 2:
#                     key = cells[0].get_text(strip=True)
#                     value = cells[1].get_text(strip=True)
#                     data[key] = value
#         return data
#
#     # Extract data from all tables
#     comms_data = extract_table_data(comms_table)
#     features_data = extract_table_data(features_table)
#     body_data = extract_table_data(body_table)
#     battery_data = extract_table_data(battery_table)
#     display_data = extract_table_data(display_table)
#     platform_data = extract_table_data(platform_table)
#
#     # Combine all data into a single dictionary
#     all_data = {
#         'Comms': comms_data,
#         'Features': features_data,
#         'Body': body_data,
#         'Battery': battery_data,
#         'Display': display_data,
#         'Platform': platform_data
#     }
#
#     return all_data

def scrape_for_gsmarena_link(query):

    api_key = "67e19fc7eccb45caac0ab4bb"
    url = "https://api.scrapingdog.com/google"
    query = query + ' - Full phone specifications - GSMArena.com'

    params = {
        "api_key": api_key,
        "query": query,
        "results": 10,
        "country": "us",
        "page": 0,
        "advance_search": "false"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data['organic_results'][0]['link']
    else:
        print(f"Request failed with status code: {response.status_code}")

# link = scrape_for_gsmarena_link('Yu Yureka')
# scrape_data_from_gsmarena(link)
