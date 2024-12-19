from urllib.parse import urlparse

from bs4 import BeautifulSoup


def extract_site_data(data):
    soup = BeautifulSoup(data, 'html.parser')

    h1, title, description = None, None, None

    if h1_find := soup.find('h1'):
        h1 = h1_find.text

    if title_find := soup.find('title'):
        title = title_find.text

    if meta_descr_find := soup.find('meta', attrs={'name': 'description'}):
        description = meta_descr_find.get('content')

    return h1, title, description


def get_url_host(url):
    parsed_url_data = urlparse(url)
    return f"{parsed_url_data.scheme}://{parsed_url_data.netloc}"
