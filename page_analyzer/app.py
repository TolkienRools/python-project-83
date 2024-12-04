from urllib.parse import urlparse
from validators.url import url
from datetime import datetime
import psycopg2
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from page_analyzer.config import SECRET_KEY, DATABASE_URL
from page_analyzer.models import (
    get_url,
    upsert_url,
    get_last_checks,
    get_checks,
    save_check
)
from page_analyzer.web_access_utils import request_to_site


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
conn = psycopg2.connect(DATABASE_URL)


@app.route('/')
def index_get():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def urls_post():
    from_url = request.form.get('url')

    if not url(from_url):
        flash("Некорректный URL", "danger")
        return render_template(
            'index.html',
            url_name=from_url
        ), 422

    parsed_url_data = urlparse(from_url)
    url_host = f"{parsed_url_data.scheme}://{parsed_url_data.netloc}"

    url_obj = {"name": url_host, "created_at": datetime.now()}
    message, status = upsert_url(conn, url_obj)
    flash(message, status)
    return redirect(url_for('urls_identity_get', url_id=url_obj['id']))


@app.route('/urls', methods=['GET'])
def urls_get():
    checks = get_last_checks(conn)
    return render_template('urls.html', checks=checks)


@app.route('/urls/<url_id>')
def urls_identity_get(url_id):
    # get data from database and send to template
    url_obj = get_url(conn, url_id)
    url_checks = get_checks(conn, url_id)
    return render_template('url.html', url=url_obj,
                           checks=url_checks)


@app.route('/urls/<url_id>/checks', methods=['POST'])
def urls_identity_checks_post(url_id):
    url_data, error_message = request_to_site(conn, url_id)
    if error_message:
        flash(error_message, 'danger')
        return redirect(url_for('urls_identity_get', id=url_id))

    save_check(conn, url_data)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('urls_identity_get', url_id=url_id))
