import requests
from datetime import datetime

from page_analyzer.models import get_url
from page_analyzer.parser import extract_site_data


def request_to_site(conn, url_id):
    url_data = get_url(conn, url_id)

    with requests.session() as session:
        try:
            response = session.get(url_data['name'])
            response.raise_for_status()
            status_code = response.status_code
            h1, title, description = extract_site_data(response.text)

            return dict(url_id=int(url_id), status_code=status_code,
                        h1=h1, title=title, description=description,
                        created_at=datetime.now()), None
        except requests.exceptions.HTTPError:
            return None, 'Произошла ошибка при проверке'
        except requests.Timeout:
            return None, 'Превышено время подключения'
        except requests.exceptions.ConnectionError:
            return None, 'Произошла ошибка подключения'
