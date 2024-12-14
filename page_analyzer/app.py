import os
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, url_for
from validators.url import url as validate_url

from page_analyzer.models import (
    connect_to_db,
    create_check,
    create_url,
    get_checks,
    get_url,
    get_url_by_name,
    get_urls,
    update_url,
)
from page_analyzer.web_access_utils import request_to_site

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


app = Flask(__name__)
app.config['DATABASE_URL'] = DATABASE_URL
app.config['SECRET_KEY'] = SECRET_KEY


@app.before_request
def before_request():
    g.db = connect_to_db(app.config['DATABASE_URL'])


@app.teardown_request
def teardown_request(exception):
    g.db.commit()
    g.db.close()


@app.route('/')
def index_get():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def urls_post():
    from_url = request.form.get('url')

    if not validate_url(from_url):
        flash("Некорректный URL", "danger")
        return render_template(
            'index.html',
            url_name=from_url
        ), 422

    parsed_url_data = urlparse(from_url)
    url_host = f"{parsed_url_data.scheme}://{parsed_url_data.netloc}"

    url_obj = {"name": url_host, "created_at": datetime.now()}

    existant_url = get_url_by_name(g.db, url_obj['name'])

    if existant_url:
        url_obj['id'] = existant_url['id']
        update_url(g.db, url_obj)
        flash("Страница уже существует", "info")
    else:
        url_obj['id'] = create_url(g.db, url_obj)
        flash("Страница успешно добавлена", "success")

    return redirect(url_for('urls_identity_get', url_id=url_obj['id']))


@app.route('/urls', methods=['GET'])
def urls_get():
    """
        Combined output from get_urls and get_checks
        using url_id and looking for last date in get_checks
        {"url_id": 1, "name": "https://bla.com",
        "created_at": "2024-12-13", "status_code": 200}
    """
    urls = get_urls(g.db)

    output_table = []
    for url in urls:
        related_checks = get_checks(g.db, url['id'])
        last_check = max(related_checks,
                         key=lambda check: check['created_at'],
                         default={})

        output_table.append({"id": url['id'], "name": url['name'],
                             "last_check": last_check.get('created_at', ''),
                             "status_code": last_check.get('status_code', '')})

    return render_template('urls.html', last_checks=output_table)


@app.route('/urls/<url_id>')
def urls_identity_get(url_id):
    url_obj = get_url(g.db, url_id)
    url_checks = get_checks(g.db, url_id)
    return render_template('url.html', url=url_obj,
                           checks=url_checks)


@app.route('/urls/<url_id>/checks', methods=['POST'])
def urls_identity_checks_post(url_id):
    url_data = get_url(g.db, url_id)
    check_data, error_message = request_to_site(url_data)
    if error_message:
        flash(error_message, 'danger')
        return redirect(url_for('urls_identity_get', url_id=url_id))

    create_check(g.db, check_data)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('urls_identity_get', url_id=url_id))
