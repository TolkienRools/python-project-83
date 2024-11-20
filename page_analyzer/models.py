from psycopg2.extras import DictCursor
from flask import flash

class UrlStorage:

    def __init__(self, conn):
        self.conn = conn

    def get_urls(self):
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("SELECT * FROM urls ORDER BY id")
            # return [dict(row) for row in curs]
            return curs.fetchall()

    def get_url(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("SELECT * FROM urls WHERE id = %s", (id, ))
            return curs.fetchone()

    def get_url_by_name(self, name):
        with self.conn.cursor(cursor_factory=DictCursor) as curs:
            curs.execute("SELECT * FROM urls WHERE name = %s", (name, ))
            return curs.fetchone()

    def save(self, url):
        existant_url = self.get_url_by_name(url['name'])

        if existant_url:
            flash("Страница уже есть", "info")
            url['id'] = existant_url['id']
            self._update(url)
        else:
            flash("Страница успешно добавлна", "success") # проверить работает ли flash ?
            self._create(url)

    def _update(self, url):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE urls SET name = %s, created_at = %s WHERE id = %s",
                (url['name'], url['created_at'], url['id'])
            )
        self.conn.commit()

    def _create(self, url):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id",
                (url['name'], url['created_at']) # can't adapt type function
            )
            id = cur.fetchone()[0]
            url['id'] = id
        self.conn.commit()