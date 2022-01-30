import logging

from utils.db_init import cursor_postgres

DATE_TMPL = '%d/%m/%y'
POSTGRES_DATE_TMPL = 'dd/mm/yy'

TABLE_NAME = 'shares'

logger = logging.getLogger(__name__)


class SharesDB:
    @classmethod
    def create_table(cls, shares_names):
        with cursor_postgres() as cur:
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            list_tables = cur.fetchall()
            logger.debug(f"list_tables = {list_tables}")
            if (TABLE_NAME,) in list_tables:
                return True

            cur.execute(f'CREATE TABLE IF NOT EXISTS {TABLE_NAME} '
                        f'(id SERIAL PRIMARY KEY, date timestamp without time zone, '
                        f'{" REAL,".join(shares_names)} REAL, UNIQUE(date))')
            return False

    @classmethod
    def insert_all(cls, share_name, data_list):
        with cursor_postgres() as cur:
            for data_item in data_list:
                cur.execute(
                    f'INSERT INTO {TABLE_NAME} (date, {share_name}) VALUES (to_timestamp(%s, %s), {data_item[1]}) '
                    f'ON CONFLICT (date) DO UPDATE SET {share_name}={data_item[1]}',
                    (data_item[0], POSTGRES_DATE_TMPL))

        logger.info(f"shares of {share_name} have been inserted")

    @classmethod
    def get_columns(cls):
        with cursor_postgres() as cur:
            cur.execute(f'SELECT * FROM information_schema.columns WHERE table_schema=%s AND table_name=%s',
                        ('public', TABLE_NAME,))
            columns = cur.fetchall()
            return columns

    @classmethod
    def get_shares_by_date(cls, date):
        time_step_shares = None
        with cursor_postgres() as cur:
            cur.execute(f'''SELECT * FROM {TABLE_NAME} WHERE date=%s''', (date,))
            time_step_shares = cur.fetchone()

        if not time_step_shares:
            logger.error(f"Не удалось получить тикеры для даты {date}. Получено: {time_step_shares}")
            exit()

        time_step_shares = time_step_shares[-10:]

        return time_step_shares
