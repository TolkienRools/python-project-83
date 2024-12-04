import os
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    g
)
from validators.url import url

from page_analyzer.models import (
    get_url,
    upsert_url,
    get_last_checks,
    get_checks,
    save_check
)
from page_analyzer.web_access_utils import request_to_site

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


@app.before_request
def before_request():
    g.db = psycopg2.connect(DATABASE_URL)


@app.teardown_request
def teardown_request(exception):
    g.db.close()


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
    message, status = upsert_url(g.db, url_obj)
    flash(message, status)
    return redirect(url_for('urls_identity_get', url_id=url_obj['id']))


@app.route('/urls', methods=['GET'])
def urls_get():
    checks = get_last_checks(g.db)
    return render_template('urls.html', checks=checks)


@app.route('/urls/<url_id>')
def urls_identity_get(url_id):
    # get data from database and send to template
    url_obj = get_url(g.db, url_id)
    url_checks = get_checks(g.db, url_id)
    return render_template('url.html', url=url_obj,
                           checks=url_checks)


@app.route('/urls/<url_id>/checks', methods=['POST'])
def urls_identity_checks_post(url_id):
    url_data, error_message = request_to_site(g.db, url_id)
    if error_message:
        flash(error_message, 'danger')
        return redirect(url_for('urls_identity_get', url_id=url_id))

    save_check(g.db, url_data)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('urls_identity_get', url_id=url_id))
