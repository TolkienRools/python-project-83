import os
from urllib.parse import urlparse

from validators.url import url
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from datetime import datetime

from .db import conn
from .models import UrlStorage

storage = UrlStorage(conn)

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
    print(url_obj)
    return redirect(url_for('urls_identity', id=url_obj['id']))


@app.route('/urls', methods=['GET'])
def urls_get():
    urls = storage.get_urls()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<id>')
def urls_identity(id):
    # get data from database and send to template
    url_obj = storage.get_url(id)
    return render_template('urls_identity.html', url=url_obj)
