from collections import namedtuple

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


def get_related_checks(conn, url_ids):
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute(
            """
            SELECT
              DISTINCT ON (url_id) url_id,
              created_at,
              status_code
            FROM
              url_checks
            WHERE
              url_id = ANY(%s)
            ORDER BY
              url_id,
              created_at DESC;
            """, (url_ids, ))
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


def get_combined_checks_data(conn):
    urls = get_urls(conn)
    checks = get_related_checks(conn, [url.id for url in urls])

    check_dict = {check.url_id: check for check in checks}

    # Create a combined list of dictionaries
    CombinedData = namedtuple('CombinedData', ['id', 'name',
                                               'last_check',
                                               'status_code'])
    CheckEmptyData = namedtuple('CheckEmptyData', ['created_at',
                                                   'status_code'])
    empty_check = CheckEmptyData('', '')
    combined_data = []
    for url in urls:
        check = check_dict.get(url.id, empty_check)
        combined_data.append(CombinedData(
            id=url.id, name=url.name,
            last_check=check.created_at,
            status_code=check.status_code
        ))
    return combined_data

