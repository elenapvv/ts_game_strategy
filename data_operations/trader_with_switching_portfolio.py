import datetime
import logging
import os
import matplotlib.pyplot as plt
import numpy as np

from algs.algorithms import Algorithms
from utils.manager_db import DATE_TMPL, SharesDB
from progress.bar import IncrementalBar

logging.basicConfig(
    format='[%(asctime)s,%(msecs)d] [%(levelname)-8s] [%(module)s:%(filename)s:%(funcName)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)
logger = logging.getLogger(__name__)

TO_SAVE_LOGS = True
TO_SAVE_PLOTS = True


def get_eta_coef():
    return 0.95


CASH = 10000

# можем тут переопределить параметр эта
Algorithms.ETA = 0.005
# eta = 100  # должно быть бесконечность для conf_hedge, но питон не "вывозит" экспоненту  в большой степени
eta = Algorithms.ETA

alpha = 0.3

# названия файлов и директорий
subdir_name = f'switching portfolio/3 - hedge with constant param without lkoh alpha={alpha}/'

filename = f'hedge with constant param eta={eta}, alpha={alpha}'
# filename = f'fixed share with variable param (initial eta={eta}, eta=ln N div delta)'

logs_dir = f'../results/{subdir_name}'
plots_dir = f'../plots/{subdir_name}'

logs_filename = f'{logs_dir}{filename}.txt'
plots_filename = f'{plots_dir}{filename}.png'

if TO_SAVE_LOGS and not os.path.isfile(logs_filename):
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    with open(logs_filename, 'w'):
        pass

if TO_SAVE_PLOTS and not os.path.isfile(plots_filename):
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    with open(plots_filename, 'w'):
        pass

MIN_DATE = datetime.datetime.strptime('01/06/07', DATE_TMPL)
MAX_DATE = datetime.datetime.strptime('15/01/22', DATE_TMPL)  # не включительно


def calculate_tickers_numbers(func_weights, func_step_shares, func_general_cash):
    func_weights_sum = sum(func_weights)
    tickers_numbers = []
    remainder = 0

    for ticker_idx in range(shares_num):
        # сколько денег готовы выделить на текущую акцию
        cash_on_ticker = func_general_cash * func_weights[ticker_idx] / func_weights_sum + remainder
        tickers_number = int(cash_on_ticker / func_step_shares[ticker_idx])
        tickers_numbers.append(tickers_number)

        # сколько не использовано денег
        remainder = cash_on_ticker - tickers_number * func_step_shares[ticker_idx]

    return tickers_numbers


if __name__ == '__main__':
    exclude_share = 3
    columns = SharesDB.get_columns()
    if not columns:
        logger.error(f"Не удалось получить названия тикеров. Получено: {columns}")
        exit()

    columns = [column[3] for column in columns[2:]]
    if exclude_share:
        time_step_shares = columns[:exclude_share] + columns[exclude_share + 1:]

    shares_num = len(columns) - 1
    general_cash_list = [CASH, ]

    weights = [1 / shares_num for _ in range(shares_num)]
    expert_gaines = [0 for _ in range(shares_num)]
    cumulative_expert_gaines = [0 for _ in range(shares_num)]
    big_delta = 0
    weights_mu = [[1 / shares_num, ] for _ in range(shares_num)]

    considered_date = MIN_DATE
    old_time_step_shares = SharesDB.get_shares_by_date(date=considered_date, exclude_share=exclude_share)
    new_time_step_shares = old_time_step_shares
    for share_idx, share in enumerate(old_time_step_shares):
        if share > CASH:
            logger.error("Выберите сумму побольше :)")
            exit()

    # probability_step = 1 / (MAX_DATE - MIN_DATE).days
    # probability = 1 - probability_step
    # logger.info(f"probability_step={probability_step}")

    number_of_share = 1
    logger.info(f"Сначала покупаем по {number_of_share} тикера(-ов)")
    number_of_shares = [1 for _ in range(shares_num)]
    considered_date = considered_date + datetime.timedelta(days=1)
    tickers_cash_lists = [[number_of_share * share, ] for share in old_time_step_shares]
    number_of_shares_lists = [[number_of_share, ] for _ in range(shares_num)]

    step = 1
    cumulative_gain = 0
    old_alg_gain = 0
    alg_gains = []
    alg_gains_for_shares_list = [[number_of_share * weights[0], ] for _ in range(shares_num)]
    general_cash = 0

    logger.info(f"ETA={eta}, alpha={alpha}")

    bar = IncrementalBar('Выполнение...', max=(MAX_DATE - MIN_DATE).days)

    while considered_date < MAX_DATE:
        logger.debug(f"-----------------------Шаг {step}-------------------------")

        expert_gaines = [number_of_shares[share_idx] * (new_time_step_shares[share_idx] -
                                                        old_time_step_shares[share_idx]) for share_idx
                         in range(shares_num)]
        cumulative_expert_gaines = [cumulative_expert_gaines[share_idx] + expert_gaines[share_idx] for share_idx
                                    in range(shares_num)]

        alg_gains_for_shares, weights = Algorithms.hedge_with_constant_param(old_weights=weights,
                                                                             shares_len=len(new_time_step_shares),
                                                                             expert_gaines=expert_gaines)

        # alg_gains_for_shares, weights = Algorithms.hedge_with_variable_param(old_weights=weights,
        #                                                                      shares_len=len(new_time_step_shares),
        #                                                                      expert_gaines=expert_gaines,
        #                                                                      cumulative_expert_gaines=cumulative_expert_gaines,
        #                                                                      eta=eta)

        # weights, big_delta, eta, alg_gain, alg_gains_for_shares, weights_mu = Algorithms.conf_hedge(eta=eta,
        #                                                                                             time_step=step,
        #                                                                                             old_weights=weights,
        #                                                                                             shares_len=len(
        #                                                                                                 new_time_step_shares),
        #                                                                                             expert_gaines=expert_gaines,
        #                                                                                             old_big_delta=big_delta,
        #                                                                                             weights_mu=weights_mu)

        # weights, big_delta, eta, alg_gain, alg_gains_for_shares = Algorithms.fixed_share_with_variable_param(eta=eta,
        #                                                                                                      time_step=step,
        #                                                                                                      old_weights=weights,
        #                                                                                                      shares_len=len(
        #                                                                                                          new_time_step_shares),
        #                                                                                                      expert_gaines=expert_gaines,
        #                                                                                                      old_big_delta=big_delta)

        # alg_gains_for_shares, weights = Algorithms.fixed_share_with_constant_param(old_weights=weights,
        #                                                                            shares_len=len(new_time_step_shares),
        #                                                                            expert_gains=expert_gaines,
        #                                                                            probability=probability)

        old_time_step_shares = new_time_step_shares
        new_time_step_shares = SharesDB.get_shares_by_date(date=considered_date, exclude_share=exclude_share)

        scalar_product = np.dot(weights, new_time_step_shares)
        weights = [weights[i] * new_time_step_shares[i] / scalar_product for i in range(shares_num)]
        weights = [alpha / shares_num + (1 - alpha) * weight for weight in weights]

        alg_gain = sum(alg_gains_for_shares)
        log_text = f"Выигрыш алгоритма Hedge на шаге {step} ({considered_date}): {alg_gain}"
        logger.debug(log_text)
        # logger.debug(f"big_delta={big_delta}, eta={eta}")
        # eta = eta * get_eta_coef()
        old_alg_gain = alg_gain
        cumulative_gain += alg_gain
        if TO_SAVE_LOGS:
            with open(logs_filename, 'a+') as f:
                f.write(f"{log_text}, денежный выигрыш: {cumulative_gain}, eta: {eta}, большая delta: {big_delta}\n")
                # f.write(f"{log_text}, всего: {cumulative_gain}, probability: {probability}\n")
        alg_gains.append(cumulative_gain)
        for share_idx in range(shares_num):
            alg_gains_for_shares_list[share_idx].append(
                alg_gains_for_shares_list[share_idx][-1] + alg_gains_for_shares[share_idx])

        # probability -= probability_step
        # if probability <= probability_step:
        #     logger.info(f"probability={probability}!")

        considered_date = considered_date + datetime.timedelta(days=1)
        step += 1

        # считаем, сколько купим акций, исходя из весов
        # general_cash = sum([number_of_shares[i] * old_time_step_shares[i] for i in range(len(old_time_step_shares))])
        # general_cash_list.append(general_cash)
        # for ticker_cash_list_idx in range(shares_num):
        #     tickers_cash_lists[ticker_cash_list_idx].append(
        #         number_of_shares[ticker_cash_list_idx] * old_time_step_shares[ticker_cash_list_idx])

        # number_of_shares = calculate_tickers_numbers(func_weights=weights, func_step_shares=old_time_step_shares,
        #                                              func_general_cash=general_cash)
        # for share_idx in range(shares_num):
        #     number_of_shares_lists[share_idx].append(number_of_shares[share_idx])

        bar.next()

    bar.finish()

    log_text = f"Кумулятивные выигрыши алгоритма Hedge для ETA={Algorithms.ETA}: {cumulative_gain}"
    logger.info(log_text)

    if TO_SAVE_LOGS:
        with open(logs_filename, 'a+') as f:
            f.write(f"{log_text}, денежный выигрыш - {general_cash}")
            logger.info("Логи с результатами сохранены")

    if TO_SAVE_PLOTS:
        plt.plot(alg_gains, label="Для всех котировок")
        for share_idx in range(shares_num):
            plt.plot(alg_gains_for_shares_list[share_idx], label=columns[share_idx])
        plt.xlabel("Шаги")
        # plt.ylabel(f"Количество акций")
        # plt.title(f"Изменение количества акций для ETA={Algorithms.ETA}")
        plt.ylabel(f"Кумулятивный выигрыш для каждого шага")
        # plt.title(f"Fixed-Share с переменным параметром")
        plt.title(f"Hedge с постоянным параметром {Algorithms.ETA} при alpha={alpha}")
        plt.legend()
        plt.savefig(plots_filename)

        logger.info("Графики с результатами сохранены")
