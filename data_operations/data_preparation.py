import datetime
import logging
import os
import pandas as pd

from utils.manager_db import SharesDB, DATE_TMPL

logging.basicConfig(
    format='[%(asctime)s,%(msecs)d] [%(levelname)-8s] [%(module)s:%(filename)s:%(funcName)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def fill_date_gaps(df):
    new_list = []
    old_datetime_item = datetime.datetime.strptime(df['<DATE>'][0], DATE_TMPL).date()
    old_item = df['<CLOSE>'][0]

    for inx, row in df.iterrows():
        datetime_item = datetime.datetime.strptime(row[0], DATE_TMPL).date()
        days_between = (datetime_item - old_datetime_item).days
        if days_between > 1:
            values_diff = (float(row[1]) - float(old_item[1])) / days_between
            for day in range(1, days_between):
                new_list.append([(old_datetime_item + datetime.timedelta(days=day)).strftime(DATE_TMPL), float(old_item[-1]) + day * values_diff])
        old_item = row
        old_datetime_item = datetime.datetime.strptime(row[0], DATE_TMPL).date()
        new_list.append([old_datetime_item.strftime(DATE_TMPL), row[-1]])

    return new_list


if __name__ == '__main__':
    data_files = os.listdir('../data')
    exists_table = SharesDB.create_table(shares_names=list(map(lambda file_name: file_name[:4], data_files)))
    logger.info(f"Таблица уже существует - {exists_table}")
    if exists_table:  # если таблица уже существует, значит, не запускаем заполнение
        exit()

    for file_name in data_files:
        with open(f'../data/{file_name}', newline='') as csvfile:
            csv_df = pd.read_csv(csvfile, delimiter=';')
            csv_df = csv_df[['<DATE>', '<CLOSE>']]
            full_list = fill_date_gaps(df=csv_df)
            SharesDB.insert_all(share_name=file_name[:4], data_list=full_list)


