import time
import psycopg2
import contextlib
import logging

from config import SHARES_DB, DATABASE_TIMEOUT_CONNECT_SEC, DATABASE_MAX_ATTEMPT

logger = logging.getLogger(__name__)


class PostgresClient:

    def __init__(self, credentials, timeout_connect_sec: int = 5, max_attempt: int = 5):
        self._credentials = credentials
        self._timeout_connect = timeout_connect_sec
        self._max_attempt = max_attempt

        # start
        self._establish_connection()

    def _establish_connection(self):

        count = 0
        while True:
            count += 1

            try:
                self._conn = psycopg2.connect(**self._credentials)
                self._conn.autocommit = True
            except psycopg2.OperationalError as ex:
                if self._cond_attempt(count=count):
                    raise Exception(ex)

                logger.info(f'Lost database connection, attempting to connect to database again {count}')
                time.sleep(self._timeout_connect)

                continue

            break

    def _cond_attempt(self, count):
        if self._max_attempt == 0:
            # если указано ноль то делать бесконечные попытки соединения
            return False

        return bool(self._max_attempt < count)

    def get_connection(self):

        count = 0
        while True:
            count += 1

            if self._conn.closed != 0:
                self._establish_connection()

            cur = self._conn.cursor()
            try:
                cur.execute('''select 1''')
            except psycopg2.OperationalError as ex:
                if self._cond_attempt(count=count):
                    raise Exception(ex)

                logger.info(f'In process query to database was lost connect. Trying to execute query again. {count}')
                time.sleep(self._timeout_connect)

                continue

            return self._conn


SharesDBClient = PostgresClient(SHARES_DB,
                                timeout_connect_sec=DATABASE_TIMEOUT_CONNECT_SEC,
                                max_attempt=DATABASE_MAX_ATTEMPT)


@contextlib.contextmanager
def cursor_postgres():
    connect = SharesDBClient.get_connection()
    try:
        with connect, connect.cursor() as cursor:
            yield cursor

    except Exception as ex:
        logger.error(ex, exc_info=True)
        connect.close()
