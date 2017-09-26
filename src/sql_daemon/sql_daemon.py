import sqlite3

__all__ = ['open_conn', 'close_conn']

db_conn = None
db_curs = None


def open_conn(path):
    db_conn = sqlite3.connect()
    db_curs = db_conn.cursor()


def close_conn():
    db_conn.close()