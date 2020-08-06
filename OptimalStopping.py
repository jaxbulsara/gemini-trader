# built-in
from statistics import mean
from logging import getLogger

# package
import constants
from Strategy import Strategy

OPTIMAL_STOPPING = "OPTIMAL_STOPPING"
STOPPING_FACTOR = 0.37

log = getLogger("gemini-trader")


class OptimalStopping(Strategy):
    name = OPTIMAL_STOPPING

    def __init__(self, *args, **kwargs):
        super(OptimalStopping, self).__init__(*args, **kwargs)
        self.price_to_beat = None
        self.start_time = None
        self.switch_time = None
        self.end_time = self.trader.cycle_start_time
        self.retry_time = 2
        self.action = self.trader.config.get("action")
        self.amount = 0

        # self.initialize()

    def initialize(self):
        self.set_price_to_beat()
        self.start_time = self.end_time
        self.switch_time = (
            self.start_time
            + self.trader.config.get(constants.PERIOD) * STOPPING_FACTOR
        )
        self.end_time = self.start_time + self.trader.config.get(
            constants.PERIOD
        )
        self.calculate_amount()
        log.debug("Initialized new cycle.")

    def run(self):
        if self.amount:
            log.debug(f"Running optimal stopping.")
            log.debug(f"\tPrice to beat = {self.price_to_beat}")
            log.debug(f"\tStart time = {self.start_time}")
            log.debug(f"\tSwitch time = {self.switch_time}")
            log.debug(f"\tEnd time = {self.end_time}")

            if self.trader.cycle_start_time < self.switch_time:
                if self.compare_price():
                    self.set_price_to_beat()
                else:
                    log.debug("LOOKING:")
                    log.debug(
                        f"\tCurrent price: {self.get_mean_bitcoin_price()}"
                    )
                    log.debug(f"\tPrice to beat: {self.price_to_beat}")

            else:
                if self.price_to_beat:
                    log.debug("READY TO LEAP:")
                    log.debug(
                        f"\tCurrent price: {self.get_mean_bitcoin_price()}"
                    )
                    log.debug(f"\tPrice to beat: {self.price_to_beat}")

                    if self.compare_price():
                        if self.action == constants.BUY:
                            bitcoin_amount = self.create_bitcoin_amount()
                        else:
                            bitcoin_amount = self.amount

                        log.info(
                            f"Placing order to {self.action} {bitcoin_amount:.8f} BTC at {(self.get_mean_bitcoin_price()):.2f} USD"
                        )

                        order = self.trader.gemini.new_order(
                            amount=f"{bitcoin_amount}",
                            price=f"{self.get_mean_bitcoin_price()}",
                            side=self.action.lower(),
                        )

                        log.debug(f"Created new order: {order}")

                        self.reset_price_to_beat()

                        log.debug("Waiting for next trading window...")

                if self.trader.cycle_start_time > self.end_time:
                    self.initialize()

    def set_price_to_beat(self):
        self.price_to_beat = self.get_mean_bitcoin_price()
        log.debug(f"Set new price to beat = {self.price_to_beat}")

    def reset_price_to_beat(self):
        self.price_to_beat = None

    def calculate_amount(self):
        amount = float(self.trader.config.get("amount"))
        stop = float(self.trader.config.get("stop"))

        if self.trader.config.get("action") == constants.BUY:
            balance = self.trader.account_balances.get(constants.USD)
        else:
            balance = self.trader.account_balances.get(constants.BTC)

        if stop >= balance:
            self.amount = 0
        else:
            self.amount = min(amount, balance - stop)

        if self.trader.config.get("action") == constants.BUY:
            log.debug(f"Set amount to buy = {self.amount} USD")
        else:
            log.debug(f"Set amount to sell = {self.amount} BTC")

    def get_mean_bitcoin_price(self):
        ask = self.trader.bitcoin_quote["ask"]
        bid = self.trader.bitcoin_quote["bid"]
        return round((mean([ask, bid])), 2)

    def update(self):
        if constants.ACTION in self.trader.changes:
            self.action = self.trader.config.get("action")
            self.end_time = self.trader.cycle_start_time
            self.initialize()

        elif constants.PERIOD in self.trader.changes:
            self.recalculate_cycle()

        if (
            constants.AMOUNT in self.trader.changes
            or constants.STOP in self.trader.changes
        ):
            self.amount = self.calculate_amount()

    def recalculate_cycle(self):
        pass

    def compare_price(self):
        if self.action == constants.BUY:
            return self.get_mean_bitcoin_price() < self.price_to_beat

        else:
            return self.get_mean_bitcoin_price() > self.price_to_beat

    def create_bitcoin_amount(self):
        return round((self.amount / (self.get_mean_bitcoin_price() + 1)), 8)

