import logging
import traceback

from math import exp

logger = logging.getLogger(__name__)


class Hedge:
    ETA = 0.001

    @classmethod
    def calculate_new_weights(cls, old_weights: list, shares: tuple, expert_losses: list):
        if not (len(old_weights) == len(shares) == len(expert_losses)):
            logger.error(f"Переданы списки разной длины\nold_weights = {old_weights}, shares = {shares}, "
                         f"expert_losses = {expert_losses}")
            exit()

        old_weights_sum = sum(old_weights)
        old_weights_normalized = [old_weight / old_weights_sum for old_weight in old_weights]

        alg_loss = sum([old_weights_normalized[i] * expert_losses[i] for i in range(len(shares))])

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
