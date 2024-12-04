from psycopg2.extras import DictCursor


def get_urls(conn):
    with conn.cursor(cursor_factory=DictCursor) as curs:
        curs.execute("SELECT * FROM urls ORDER BY id")
        return curs.fetchall()


def get_url(conn, id):
    with conn.cursor(cursor_factory=DictCursor) as curs:
        curs.execute("SELECT * FROM urls WHERE id = %s", (id, ))
        return curs.fetchone()


def get_url_by_name(conn, name):
    with conn.cursor(cursor_factory=DictCursor) as curs:
        curs.execute("SELECT * FROM urls WHERE name = %s", (name, ))
        return curs.fetchone()


def update_url(conn, url):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE urls SET name = %s, created_at = %s WHERE id = %s",
            (url['name'], url['created_at'], url['id'])
        )
    conn.commit()


def create_url(conn, url):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO urls (name, created_at)
            VALUES (%s, %s) RETURNING id""",
            (url['name'], url['created_at'])
        )
        id = cur.fetchone()[0]
        url['id'] = id
    conn.commit()


def upsert_url(conn, url):
    existant_url = get_url_by_name(conn, url['name'])

    if existant_url:
        url['id'] = existant_url['id']
        update_url(conn, url)
        return "Страница уже существует", "info"
    else:
        create_url(conn, url)
        return "Страница успешно добавлена", "success"


def get_checks(conn, url_id):
    with conn.cursor(cursor_factory=DictCursor) as curs:
        curs.execute("""SELECT * FROM url_checks
        WHERE url_id = %s ORDER BY id""", (url_id, ))
        # return [dict(row) for row in curs]
        return curs.fetchall()


def get_last_checks(conn):
    with conn.cursor(cursor_factory=DictCursor) as curs:
        curs.execute("""SELECT urls.id, urls.name,
        MAX(url_checks.created_at) AS last_check,
        url_checks.status_code AS status_code FROM url_checks
        RIGHT JOIN urls ON url_checks.url_id = urls.id
        GROUP BY urls.id, urls.name, url_checks.status_code
        ORDER BY urls.id""")
        return curs.fetchall()


def save_check(conn, url_check):
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO url_checks (url_id, status_code,
            h1, title, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (url_check['url_id'], url_check['status_code'],
             url_check['h1'], url_check['title'],
             url_check['description'], url_check['created_at'])
        )
        id = cur.fetchone()[0]
        url_check['id'] = id
    conn.commit()
