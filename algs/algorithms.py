import logging

from math import exp, isinf

logger = logging.getLogger(__name__)


class Algorithms:
    ETA = 0.0001  # оптимально

    @classmethod
    def hedge_with_constant_param(cls, old_weights: list, shares: tuple, expert_gaines: list):
        if not (len(old_weights) == len(shares) == len(expert_gaines)):
            logger.error(f"Переданы списки разной длины\nold_weights = {old_weights}, shares = {shares}, "
                         f"expert_gaines = {expert_gaines}")
            exit()

        old_weights_sum = sum(old_weights)
        if isinf(old_weights_sum):
            logger.error("Сумма весов равна бесконечности")
            exit()

        old_weights_normalized = [old_weight / old_weights_sum for old_weight in old_weights]

        alg_gains_for_shares = [old_weights_normalized[i] * expert_gaines[i] for i in range(len(shares))]
        # alg_gain = sum(alg_gains_for_shares)

        logger.debug(f"alg_gains_for_shares={alg_gains_for_shares},\nold_weights_sum={old_weights_sum},\n"
                     f"old_weights_normalized={old_weights_normalized},\nold_weights={old_weights}"
                     f"\nexpert_gaines={expert_gaines}")

        new_weights = []
        try:
            for i in range(len(shares)):
                new_weights.append(old_weights[i] * exp(cls.ETA * expert_gaines[i]))

        except OverflowError:
            logger.error(f"Слишком большое для экспоненты число: {cls.ETA * expert_gaines[len(new_weights)]}")
            raise
        except Exception:
            raise

        return alg_gains_for_shares, new_weights

    @classmethod
    def hedge_with_variable_param(cls, eta, old_weights: list, shares: tuple, expert_gaines: list,
                                  cumulative_expert_gaines: list):
        if not (len(old_weights) == len(shares) == len(expert_gaines)):
            logger.error(f"Переданы списки разной длины\nold_weights = {old_weights}, shares = {shares}, "
                         f"expert_gaines = {expert_gaines}")
            exit()

        old_weights_sum = sum(old_weights)
        if isinf(old_weights_sum):
            logger.error("Сумма весов равна бесконечности")
            exit()

        old_weights_normalized = [old_weight / old_weights_sum for old_weight in old_weights]

        alg_gains_for_shares = [old_weights_normalized[i] * expert_gaines[i] for i in range(len(shares))]
        # alg_gain = sum(alg_gains_for_shares)

        logger.debug(f"alg_gains_for_shares={alg_gains_for_shares},\nold_weights_sum={old_weights_sum},\n"
                     f"old_weights_normalized={old_weights_normalized},\nold_weights={old_weights}"
                     f"\nexpert_gaines={expert_gaines}")

        new_weights = []
        try:
            for i in range(len(shares)):
                new_weights.append(old_weights[i] * exp(eta * cumulative_expert_gaines[i]))

        except OverflowError:
            logger.error(f"Слишком большое для экспоненты число: {eta * expert_gaines[len(new_weights)]}")
            raise
        except Exception:
            raise

        return alg_gains_for_shares, new_weights

    @classmethod
    def fixed_share(cls, old_weights: list, shares: tuple, expert_losses: list, probabilities: list):
        if not (len(old_weights) == len(shares) == len(expert_losses)):
            logger.error(f"Переданы списки разной длины\nold_weights = {old_weights}, shares = {shares}, "
                         f"expert_losses = {expert_losses}")
            exit()

        old_weights_sum = sum(old_weights)
        if isinf(old_weights_sum):
            logger.error("Сумма весов равна бесконечности")
            exit()

        old_weights_normalized = [old_weight / old_weights_sum for old_weight in old_weights]

        alg_loss = sum([old_weights_normalized[i] * expert_losses[i] for i in range(len(shares))])

        logger.debug(f"alg_loss={alg_loss},\nold_weights_sum={old_weights_sum},\n"
                     f"old_weights_normalized={old_weights_normalized},\nold_weights={old_weights}"
                     f"\nexpert_losses={expert_losses}")

        new_weights = []
        try:
            for i in range(len(shares)):
                overridden_weight = old_weights[i] * exp(- cls.ETA * expert_losses[i])
                pool = sum([probabilities[i] * expert_losses[i] for i in range(len(shares))])
                new_weights.append((1 - probabilities[i]) * overridden_weight + 1 / (len(shares) - 1))

        except OverflowError:
            logger.error(f"Слишком большое для экспоненты число: {- cls.ETA * expert_losses[len(new_weights)]}")
            raise
        except Exception:
            raise

        return alg_loss, new_weights
