import datetime
import logging
import os

from algs.hedge import Hedge
from utils.manager_db import DATE_TMPL, SharesDB

logs_filename = f'../results/ETA={Hedge.ETA}, time={datetime.datetime.now().strftime("%d.%m.%Y %H.%M.%S")}.log'

if not os.path.isfile(logs_filename):
    with open(logs_filename, 'w'):
        pass

logging.basicConfig(
    format='[%(asctime)s,%(msecs)d] [%(levelname)-8s] [%(module)s:%(filename)s:%(funcName)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)
logger = logging.getLogger(__name__)

MIN_DATE = datetime.datetime.strptime('01/06/07', DATE_TMPL)
MAX_DATE = datetime.datetime.strptime('15/01/22', DATE_TMPL)  # не включительно

if __name__ == '__main__':
    columns = SharesDB.get_columns()
    if not columns:
        logger.error(f"Не удалось получить названия тикеров. Получено: {columns}")
        exit()

    shares_num = len(columns) - 2
    weights = [1 / shares_num for _ in range(shares_num)]
    expert_losses = [0 for _ in range(shares_num)]

    considered_date = MIN_DATE
    old_time_step_shares = SharesDB.get_shares_by_date(date=considered_date)
    considered_date = considered_date + datetime.timedelta(days=1)

    step = 1
    cumulative_loss = 0

    logger.info(f"ETA={Hedge.ETA}")

    while considered_date < MAX_DATE:
        new_time_step_shares = SharesDB.get_shares_by_date(date=considered_date)
        expert_losses = [new_time_step_shares[share_idx] - old_time_step_shares[share_idx] for share_idx in
                         range(shares_num)]

        alg_loss, weights = Hedge.calculate_new_weights(old_weights=weights, shares=new_time_step_shares,
                                                        expert_losses=expert_losses)

        log_text = f"Потери алгоритма Hedge на шаге {step} ({considered_date}): {alg_loss}"
        logger.debug(log_text)
        with open(logs_filename, 'a+') as f:
            f.write(f"{log_text}\n")
        cumulative_loss += alg_loss

        considered_date = considered_date + datetime.timedelta(days=1)
        old_time_step_shares = new_time_step_shares
        step += 1

    log_text = f"Кумулятивные потери алгоритма Hedge для ETA={Hedge.ETA}: {cumulative_loss}"
    logger.info(log_text)
    with open(logs_filename, 'a+') as f:
        f.write(f"\n{log_text}")
