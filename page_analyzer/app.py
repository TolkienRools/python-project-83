import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, url_for
from validators.url import url as validate_url

from page_analyzer import models
from page_analyzer.parser import get_url_host
from page_analyzer.web_access_utils import request_to_site

load_dotenv()


app = Flask(__name__)
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.before_request
def before_request():
    g.db = models.connect_to_db(app.config['DATABASE_URL'])


@app.teardown_request
def teardown_request(exception):
    g.db.commit()
    g.db.close()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


@app.route('/')
def get_index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def create_url():
    from_url = request.form.get('url')

    if not validate_url(from_url):
        flash("Некорректный URL", "danger")
        return render_template(
            'index.html',
            url_name=from_url
        ), 422

    url_host = get_url_host(from_url)
    existing_url = models.get_url_by_name(g.db, url_host)

    if existing_url:
        url_id = existing_url.id
        flash("Страница уже существует", "info")
    else:
        url_data = {"name": url_host,
                    "created_at": datetime.now()}
        url_id = models.create_url(g.db, url_data)
        flash("Страница успешно добавлена", "success")

    return redirect(url_for('get_url', url_id=url_id))


@app.route('/urls', methods=['GET'])
def get_urls():
    """
        Combined output from get_urls and get_checks
        using url_id and looking for last date in get_checks
        CombinedData(
            id=url.id, name=url.name,
            last_check=check.created_at,
            status_code=check.status_code
        )
    """
    combined_data = models.get_combined_checks_data(g.db)
    return render_template('urls.html', last_checks=combined_data)


@app.route('/urls/<url_id>')
def get_url(url_id):
    new_url = models.get_url(g.db, url_id)
    checks = models.get_checks(g.db, url_id)
    return render_template('url.html', url=new_url,
                           checks=checks)


@app.route('/urls/<url_id>/checks', methods=['POST'])
def create_url_check(url_id):
    url_data = models.get_url(g.db, url_id)
    check_data, error_message = request_to_site(url_data)
    if error_message:
        flash(error_message, 'danger')
        return redirect(url_for('get_url', url_id=url_id))

    models.create_check(g.db, check_data)
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url', url_id=url_id))
