import requests
from .models import UrlStorage
from .parser import extract_site_data


def request_to_site(url_check):
    store = UrlStorage()
    url_data = store.get_url(url_check['url_id'])

    with requests.session() as session:
        try:
            response = session.get(url_data['name'])
            response.raise_for_status()
            url_check['status_code'] = response.status_code
            extract_site_data(response.text, url_check)
        except requests.exceptions.HTTPError:
            return 'Произошла ошибка при проверке'
        except requests.Timeout:
            return 'Превышено время подключения'
        except requests.exceptions.ConnectionError:
            return 'Произошла ошибка подключения'
