import requests


def get_country(lat, lon):
    url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2&accept-language=ua&zoom=18'
    try:
        result = requests.get(url=url, headers={'User-Agent': 'Chrome/123.0.0.0 Safari/537.36'})
        result_json = result.json()
        result_str = ''

        if 'shop' in result_json['address']:
            result_str += f"{result_json['address']['shop']}, "
        if 'road' in result_json['address']:
            result_str += result_json['address']['road']
        if 'house_number' in result_json['address']:
            result_str += f", {result_json['address']['house_number']}"

        return result_str
    except:
        return None

    # {'place_id': 203132121, 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright',
    #  'osm_type': 'way', 'osm_id': 505417558, 'lat': '49.7944938', 'lon': '24.018853352699658', 'category': 'leisure',
    #  'type': 'playground', 'place_rank': 30, 'importance': 9.99999999995449e-06, 'addresstype': 'leisure', 'name': '',
    #  'display_name': 'вулиця Михайла Максимовича, Боднарівка, Сихівський район, Львів, Львівська міська громада, Львівський район, Львівська область, 79031, Україна',
    #  'address': {'road': 'вулиця Михайла Максимовича', 'suburb': 'Боднарівка', 'borough': 'Сихівський район',
    #              'city': 'Львів', 'municipality': 'Львівська міська громада', 'district': 'Львівський район',
    #              'state': 'Львівська область', 'ISO3166-2-lvl4': 'UA-46', 'postcode': '79031', 'country': 'Україна',
    #              'country_code': 'ua'}, 'boundingbox': ['49.7943378', '49.7946497', '24.0187579', '24.0189488']}

# {'place_id': 201980208, 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright',
#  'osm_type': 'relation', 'osm_id': 8781167, 'lat': '49.87053195', 'lon': '24.022953991519174', 'category': 'shop',
#  'type': 'mall', 'place_rank': 30, 'importance': 9.99999999995449e-06, 'addresstype': 'shop', 'name': 'Spartak',
#  'display_name': 'Spartak, 1б, вулиця Гетьмана Івана Мазепи, Замарстинів, Шевченківський район, Львів, Львівська міська громада, Львівський район, Львівська область, 79068, Україна',
#  'address': {'shop': 'Spartak', 'house_number': '1б', 'road': 'вулиця Гетьмана Івана Мазепи', 'suburb': 'Замарстинів', 'borough': 'Шевченківський район',
#              'city': 'Львів', 'municipality': 'Львівська міська громада', 'district': 'Львівський район', 'state': 'Львівська область', 'ISO3166-2-lvl4': 'UA-46',
#              'postcode': '79068', 'country': 'Україна', 'country_code': 'ua'}, 'boundingbox': ['49.8698964', '49.8713597', '24.0220009', '24.0239186']}