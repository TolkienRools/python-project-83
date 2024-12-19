from psycopg2 import connect
from psycopg2.extras import NamedTupleCursor


def connect_to_db(db_url):
    return connect(db_url)


def get_urls(conn):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            """
            SELECT
              *
            FROM
              urls
            ORDER BY
              id;
            """)
        return curs.fetchall()


def get_url(conn, url_id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            """
            SELECT
              *
            FROM
              urls
            WHERE
              id = %s;
            """, (url_id, ))
        return curs.fetchone()


def get_url_by_name(conn, name):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            """
            SELECT
              *
            FROM
              urls
            WHERE
              name = %s;
            """, (name, ))
        return curs.fetchone()


def update_url(conn, url):
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE
              urls
            SET
              name = %s,
              created_at = %s
            WHERE
              id = %s;
            """,
            (url['name'], url['created_at'], url['id'])
        )


def create_url(conn, url):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO urls (name, created_at)
            VALUES
              (%s, %s) RETURNING id;
            """,
            (url['name'], url['created_at'])
        )
        url_id = cur.fetchone()[0]
    return url_id


def get_checks(conn, url_id):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            """
            SELECT
              *
            FROM
              url_checks
            WHERE
              url_id = %s
            ORDER BY
              id;
            """, (url_id, ))
        return curs.fetchall()


def create_check(conn, url_check):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO url_checks (
              url_id, status_code, h1, title, description,
              created_at
            )
            VALUES
              (%s, %s, %s, %s, %s, %s) RETURNING id;
            """,
            (url_check['url_id'], url_check['status_code'],
             url_check['h1'], url_check['title'],
             url_check['description'], url_check['created_at'])
        )
        check_id = cur.fetchone()[0]
        return check_id
