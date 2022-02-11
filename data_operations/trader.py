import datetime
import logging
import os
import matplotlib.pyplot as plt

from algs.hedge import Hedge
from utils.manager_db import DATE_TMPL, SharesDB
from progress.bar import IncrementalBar

logging.basicConfig(
    format='[%(asctime)s,%(msecs)d] [%(levelname)-8s] [%(module)s:%(filename)s:%(funcName)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)
logger = logging.getLogger(__name__)

TO_SAVE_LOGS = True
TO_SAVE_PLOTS = True

# можем тут переопределить параметр эта
Hedge.ETA = 0.00001

CASH = 10000

# logs_filename = f'../results/ETA={Hedge.ETA}, time={datetime.datetime.now().strftime("%d.%m.%Y %H.%M.%S")}.txt'
filename = f'ETA={Hedge.ETA}, CASH={CASH} with calculated number of shares'
subdir_name = 'with calculated number of shares - 4/'
logs_filename = f'../results/{subdir_name}{filename}.txt'
plots_filename = f'../plots/{subdir_name}{filename}.png'

if TO_SAVE_LOGS and not os.path.isfile(logs_filename):
    with open(logs_filename, 'w'):
        pass

if TO_SAVE_PLOTS and not os.path.isfile(plots_filename):
    with open(plots_filename, 'w'):
        pass

MIN_DATE = datetime.datetime.strptime('01/06/07', DATE_TMPL)
MAX_DATE = datetime.datetime.strptime('15/01/22', DATE_TMPL)  # не включительно


def calculate_tickers_numbers(func_weights, func_step_shares):
    func_weights_sum = sum(func_weights)
    tickers_numbers = []
    remainder = 0

    for ticker_idx in range(shares_num):
        # сколько денег готовы выделить на текущую акцию
        cash_on_ticker = CASH * func_weights[ticker_idx] / func_weights_sum + remainder
        tickers_number = int(cash_on_ticker / func_step_shares[ticker_idx])
        tickers_numbers.append(tickers_number)

        # сколько не использовано денег
        remainder = cash_on_ticker - tickers_number * func_step_shares[ticker_idx]

    return tickers_numbers


if __name__ == '__main__':
    columns = SharesDB.get_columns()
    if not columns:
        logger.error(f"Не удалось получить названия тикеров. Получено: {columns}")
        exit()

    shares_num = len(columns) - 2
    weights = [1 / shares_num for _ in range(shares_num)]
    expert_losses = [0 for _ in range(shares_num)]

    considered_date = MIN_DATE
    old_time_step_shares = SharesDB.get_shares_by_date(date=considered_date, shares_num=shares_num)
    for share_idx, share in enumerate(old_time_step_shares):
        if share > CASH:
            logger.error("Выберите сумму побольше :)")
            exit()

    number_of_share = int(CASH / sum(old_time_step_shares))
    logger.info(f"Сначала покупаем по {number_of_share} тикера(-ов)")
    number_of_shares = [number_of_share for _ in range(shares_num)]
    considered_date = considered_date + datetime.timedelta(days=1)

    step = 1
    cumulative_loss = 0
    alg_losses = []

    logger.info(f"ETA={Hedge.ETA}")

    bar = IncrementalBar('Выполнение...', max=(MAX_DATE - MIN_DATE).days)

    while considered_date < MAX_DATE:

        new_time_step_shares = SharesDB.get_shares_by_date(date=considered_date, shares_num=shares_num)

        expert_losses = [number_of_shares[share_idx] * (new_time_step_shares[share_idx] -
                                                        old_time_step_shares[share_idx]) for share_idx
                         in range(shares_num)]

        alg_loss, weights = Hedge.calculate_new_weights(old_weights=weights, shares=new_time_step_shares,
                                                        expert_losses=expert_losses)

        log_text = f"Потери алгоритма Hedge на шаге {step} ({considered_date}): {alg_loss}"
        logger.debug(log_text)
        cumulative_loss += alg_loss
        if TO_SAVE_LOGS:
            with open(logs_filename, 'a+') as f:
                f.write(f"{log_text}, всего: {cumulative_loss}\n")
        alg_losses.append(cumulative_loss)

        considered_date = considered_date + datetime.timedelta(days=1)
        old_time_step_shares = new_time_step_shares
        step += 1

        # считаем, сколько купим акций, исходя из весов
        number_of_shares = calculate_tickers_numbers(func_weights=weights, func_step_shares=old_time_step_shares)

        # print(old_time_step_shares, number_of_shares)

        bar.next()

    bar.finish()

    log_text = f"Кумулятивные потери алгоритма Hedge для ETA={Hedge.ETA}: {cumulative_loss}"
    logger.info(log_text)

    if TO_SAVE_LOGS:
        with open(logs_filename, 'a+') as f:
            f.write(f"\n{log_text}")
            logger.info("Логи с результатами сохранены")

    if TO_SAVE_PLOTS:
        plt.plot(alg_losses)
        plt.xlabel("Шаги")
        plt.ylabel(f"Кумулятивные потери для каждого шага")
        plt.title(f"Кумулятивные потери алгоритма Hedge для ETA={Hedge.ETA}")
        plt.savefig(plots_filename)

        logger.info("Графики с результатами сохранены")
