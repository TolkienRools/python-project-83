import os
from urllib.parse import urlparse

from validators.url import url
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from datetime import datetime

from .models import UrlStorage, UrlCheck
from .web_access_utils import request_to_site

storage = UrlStorage()
checker = UrlCheck()

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def urls_post():
    from_url = request.form.get('url')

    if not url(from_url):
        flash("Некорректный URL", "error")
        return render_template('index.html', url_name=from_url)

    parsed_url_data = urlparse(from_url)
    from_url = f"{parsed_url_data.scheme}://{parsed_url_data.netloc}"

    url_obj = {"name": from_url, "created_at": datetime.now()}
    storage.save(url_obj)
    return redirect(url_for('urls_identity', id=url_obj['id']))


@app.route('/urls', methods=['GET'])
def urls_get():
    checks = checker.get_last_checks()
    return render_template('urls.html', checks=checks)


@app.route('/urls/<id>')
def urls_identity(id):
    # get data from database and send to template
    url_obj = storage.get_url(id)
    url_check_objs = checker.get_checks(id)
    return render_template('url.html', url=url_obj,
                           checks=url_check_objs)


@app.route('/urls/<id>/checks', methods=['POST'])
def urls_identity_checks(id):
    url_check_obj = {"url_id": int(id), "status_code": None,
                     "h1": None, "title": None, "description": None,
                     "created_at": datetime.now()}

    error_message = request_to_site(url_check_obj)
    if error_message:
        flash(error_message, 'error')
        return redirect(url_for('urls_identity', id=id))

    checker.save(url_check_obj)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('urls_identity', id=id))
