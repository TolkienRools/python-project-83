from bs4 import BeautifulSoup


def extract_site_data(data, url_check):
    soup = BeautifulSoup(data, 'html.parser')

    if h1 := soup.find('h1'):
        url_check['h1'] = h1.text

    if title := soup.find('title'):
        url_check['title'] = title.text

    if meta_descr := soup.find('meta', attrs={'name': 'description'}):
        url_check['description'] = meta_descr.get('content')
