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

        if not result_str:
            print(result_json)
            result_str = result_json["display_name"]

        return result_str
    except:
        return None
