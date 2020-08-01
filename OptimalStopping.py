# built-in
from logging import getLogger

# package
from GeminiTrader import GeminiTrader

log = getLogger("gemini-trader")


class OptimalStopping:
    self: GeminiTrader

    def __init__(self):
        self.optimal_stopping_parameters = {
            "price_to_beat": None,
            "start_time": None,
            "end_time": None,
        }

    def optimal_stopping(self):
        pass
