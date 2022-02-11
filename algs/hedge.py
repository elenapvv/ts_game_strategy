import logging

from math import exp, isinf

logger = logging.getLogger(__name__)


class Hedge:
    ETA = 0.001  # оптимально

    @classmethod
    def calculate_new_weights(cls, old_weights: list, shares: tuple, expert_losses: list):
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
                new_weights.append(old_weights[i] * exp(- cls.ETA * expert_losses[i]))

        except OverflowError:
            logger.error(f"Слишком большое для экспоненты число: {- cls.ETA * expert_losses[len(new_weights)]}")
            raise
        except Exception:
            raise

        return alg_loss, new_weights
