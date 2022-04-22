import logging
import math
import numpy as np

from math import exp, isinf

logger = logging.getLogger(__name__)


class Algorithms:
    ETA = 0.0001  # оптимально

    @classmethod
    def hedge_with_constant_param(cls, old_weights: list, shares_len: int, expert_gaines: list):
        if not (len(old_weights) == shares_len == len(expert_gaines)):
            logger.error(f"Переданы списки разной длины\nold_weights = {old_weights}, shares_len = {shares_len}, "
                         f"expert_gaines = {expert_gaines}")
            exit()

        old_weights_sum = sum(old_weights)
        if isinf(old_weights_sum):
            logger.error("Сумма весов равна бесконечности")
            exit()

        old_weights_normalized = [old_weight / old_weights_sum for old_weight in old_weights]

        alg_gains_for_shares = [old_weights_normalized[i] * expert_gaines[i] for i in range(shares_len)]
        # alg_gain = sum(alg_gains_for_shares)

        logger.debug(f"alg_gains_for_shares={alg_gains_for_shares},\nold_weights_sum={old_weights_sum},\n"
                     f"old_weights_normalized={old_weights_normalized},\nold_weights={old_weights}"
                     f"\nexpert_gaines={expert_gaines}")

        new_weights = []
        try:
            for i in range(shares_len):
                new_weights.append(old_weights[i] * exp(cls.ETA * expert_gaines[i]))

        except OverflowError:
            logger.error(f"Слишком большое для экспоненты число: {cls.ETA * expert_gaines[len(new_weights)]}")
            raise
        except Exception:
            raise

        return alg_gains_for_shares, new_weights

    @classmethod
    def hedge_with_variable_param(cls, eta, old_weights: list, shares_len: int, expert_gaines: list,
                                  cumulative_expert_gaines: list):
        if not (len(old_weights) == shares_len == len(expert_gaines)):
            logger.error(f"Переданы списки разной длины\nold_weights = {old_weights}, shares_len = {shares_len}, "
                         f"expert_gaines = {expert_gaines}")
            exit()

        old_weights_sum = sum(old_weights)
        if isinf(old_weights_sum):
            logger.error("Сумма весов равна бесконечности")
            exit()

        old_weights_normalized = [old_weight / old_weights_sum for old_weight in old_weights]

        alg_gains_for_shares = [old_weights_normalized[i] * expert_gaines[i] for i in range(shares_len)]
        # alg_gain = sum(alg_gains_for_shares)

        logger.debug(f"alg_gains_for_shares={alg_gains_for_shares},\nold_weights_sum={old_weights_sum},\n"
                     f"old_weights_normalized={old_weights_normalized},\nold_weights={old_weights}"
                     f"\nexpert_gaines={expert_gaines}")

        new_weights = []
        try:
            for i in range(shares_len):
                new_weights.append(old_weights[i] * exp(eta * cumulative_expert_gaines[i]))

        except OverflowError:
            logger.error(f"Слишком большое для экспоненты число: {eta * expert_gaines[len(new_weights)]}")
            raise
        except Exception:
            raise

        return alg_gains_for_shares, new_weights

    @classmethod
    def conf_hedge(cls, eta, time_step, old_weights: list, shares_len: int, expert_gaines: list, old_big_delta,
                   weights_mu: list):
        if not (len(old_weights) == shares_len == len(expert_gaines)):
            logger.error(f"Переданы списки разной длины\nold_weights = {old_weights}, shares_len = {shares_len}, "
                         f"expert_gaines = {expert_gaines}")
            exit()

        if not (time_step == len(weights_mu[0])):
            logger.error(f"Переданы параметры разной длины\n"
                         f"time_step = {time_step}, len(weights_mu[0]) = {len(weights_mu[0])}")
            exit()

        old_weights_sum = sum(old_weights)
        if isinf(old_weights_sum):
            logger.error("Сумма весов равна бесконечности")
            exit()

        old_weights_normalized = [old_weight / old_weights_sum for old_weight in old_weights]

        alg_gain = np.dot(old_weights_normalized, expert_gaines)
        alg_gains_for_shares = [old_weights_normalized[i] * expert_gaines[i] for i in range(shares_len)]

        logger.debug(f"alg_gain={alg_gain},\nold_weights_sum={old_weights_sum},\n"
                     f"old_weights_normalized={old_weights_normalized},\nold_weights={old_weights}"
                     f"\nexpert_gaines={expert_gaines}")

        old_weights_mu_sum = sum(
            [old_weights[i] * exp(eta * (expert_gaines[i] + alg_gain)) for i in range(shares_len)])
        # old_weights_mu_sum = 0
        # for i in range(shares_len):
        #     old_weights_mu_sum += old_weights[i] * exp(eta * (expert_gaines[i] + alg_gain))
        #     logger.debug(exp(eta * (expert_gaines[i] + alg_gain)))
        #     logger.debug(eta * (expert_gaines[i] + alg_gain))

        logger.debug(f"old_weights_mu_sum={old_weights_mu_sum}")
        old_weights_mu = []
        beta = 1 / time_step
        new_weights = []
        try:
            for i in range(shares_len):
                old_weights_mu.append((old_weights[i] * exp(eta * (expert_gaines[i] + alg_gain))) / old_weights_mu_sum)
                weights_mu[i].append(old_weights_mu[i])
                new_weights.append(sum([beta * weights_mu[i][j] for j in range(time_step)]))

                logger.debug(f"old_weights_mu[i]={old_weights_mu[i]}, new_weights[i]={new_weights[i]}")

        except OverflowError:
            logger.error(f"Слишком большое для экспоненты число: {eta * expert_gaines[len(new_weights)]}")
            raise
        except Exception:
            raise

        mixgain = 1 / eta * math.log(sum([old_weights[i] * exp(eta * expert_gaines[i]) for i in range(shares_len)]))
        small_delta = mixgain - alg_gain
        new_big_delta = old_big_delta + small_delta
        new_eta = 1 / new_big_delta

        if mixgain < alg_gain:
            logger.error(f"mixgain < alg_gain! mixgain={mixgain}, alg_gain={alg_gain}")
            exit()

        return new_weights, new_big_delta, new_eta, alg_gain, alg_gains_for_shares, weights_mu

    @classmethod
    def fixed_share_with_variable_param(cls, eta, time_step, old_weights: list, shares_len: int, expert_gaines: list,
                                        old_big_delta):
        if not (len(old_weights) == shares_len == len(expert_gaines)):
            logger.error(f"Переданы списки разной длины\nold_weights = {old_weights}, shares_len = {shares_len}, "
                         f"expert_gaines = {expert_gaines}")
            exit()

        old_weights_sum = sum(old_weights)
        if isinf(old_weights_sum):
            logger.error("Сумма весов равна бесконечности")
            exit()

        old_weights_normalized = [old_weight / old_weights_sum for old_weight in old_weights]

        alg_gain = np.dot(old_weights_normalized, expert_gaines)
        alg_gains_for_shares = [old_weights_normalized[i] * expert_gaines[i] for i in range(shares_len)]

        logger.debug(f"alg_gain={alg_gain},\nold_weights_sum={old_weights_sum},\n"
                     f"old_weights_normalized={old_weights_normalized},\nold_weights={old_weights}"
                     f"\nexpert_gaines={expert_gaines}")

        old_weights_mu_sum = sum(
            [old_weights[i] * exp(eta * (expert_gaines[i] + alg_gain)) for i in range(shares_len)])
        # old_weights_mu_sum = 0
        # for i in range(shares_len):
        #     old_weights_mu_sum += old_weights[i] * exp(eta * (expert_gaines[i] + alg_gain))
        #     logger.debug(exp(eta * (expert_gaines[i] + alg_gain)))
        #     logger.debug(eta * (expert_gaines[i] + alg_gain))

        logger.debug(f"old_weights_mu_sum={old_weights_mu_sum}")

        alpha = 1 / (time_step + 1)
        beta = [alpha, ]
        beta.extend([0 for _ in range(time_step - 2)])
        beta.append(1 - alpha)

        new_weights = []
        try:
            for i in range(shares_len):
                old_weights_mu = (old_weights[i] * exp(eta * (expert_gaines[i] + alg_gain))) / old_weights_mu_sum
                new_weights.append(alpha / shares_len + (1 - alpha) * old_weights_mu)

                logger.debug(f"old_weights_mu={old_weights_mu}, new_weights[i]={new_weights[i]}")

        except OverflowError:
            logger.error(f"Слишком большое для экспоненты число: {eta * expert_gaines[len(new_weights)]}")
            raise
        except Exception:
            raise

        mixgain = 1 / eta * math.log(sum([old_weights[i] * exp(eta * expert_gaines[i]) for i in range(shares_len)]))
        small_delta = mixgain - alg_gain
        new_big_delta = old_big_delta + small_delta
        new_eta = math.log(shares_len) / new_big_delta

        if mixgain < alg_gain:
            logger.error(f"mixgain < alg_gain! mixgain={mixgain}, alg_gain={alg_gain}, time_step={time_step}")
            exit()

        return new_weights, new_big_delta, new_eta, alg_gain, alg_gains_for_shares

    @classmethod
    def fixed_share_with_constant_param(cls, old_weights: list, shares_len: int, expert_gains: list,
                                        probability: float):
        if not (len(old_weights) == shares_len == len(expert_gains)):
            logger.error(f"Переданы списки разной длины\nold_weights = {old_weights}, shares_len = {shares_len}, "
                         f"expert_gains = {expert_gains}")
            exit()

        old_weights_sum = sum(old_weights)
        if isinf(old_weights_sum):
            logger.error("Сумма весов равна бесконечности")
            exit()

        old_weights_normalized = [old_weight / old_weights_sum for old_weight in old_weights]

        alg_gains_for_shares = [old_weights_normalized[i] * expert_gains[i] for i in range(shares_len)]

        logger.debug(f"alg_gains_for_shares={alg_gains_for_shares},\nold_weights_sum={old_weights_sum},\n"
                     f"old_weights_normalized={old_weights_normalized},\nold_weights={old_weights}"
                     f"\nexpert_gains={expert_gains}")

        new_weights = []
        try:
            for i in range(shares_len):
                overridden_weight = old_weights[i] * exp(cls.ETA * expert_gains[i])
                pool = sum([probability * overridden_weight for _ in range(shares_len)])
                new_weights.append((1 - probability) * overridden_weight + 1 / (shares_len - 1) * (
                        pool - probability * overridden_weight))

        except OverflowError:
            logger.error(f"Слишком большое для экспоненты число: {- cls.ETA * expert_gains[len(new_weights)]}")
            raise
        except Exception:
            raise

        return alg_gains_for_shares, new_weights
