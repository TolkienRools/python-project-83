import requests
from .models import UrlStorage


def get_site_data(url_check):
    store = UrlStorage()
    url_data = store.get_url(url_check['url_id'])

    with requests.session() as session:
        try:
            response = session.get(url_data['name'])
            response.raise_for_status()
            url_check['status_code'] = response.status_code
        except requests.exceptions.HTTPError:
            return 'Произошла ошибка при проверке'
        except requests.Timeout:
            return 'Превышено время подключения'
        except requests.exceptions.ConnectionError:
            return 'Произошла ошибка подключения'
