# built-in
from datetime import datetime
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
        self.end_time = None
        self.amount = 0

    def initialize(self):
        log.info("Initializing new cycle...")
        self.set_price_to_beat()
        self.set_start_time()
        self.set_switch_time()
        self.set_end_time()
        self.calculate_amount()

    def run(self):
        if self.amount:
            self.optimal_stopping()

        else:
            self.calculate_amount()

            if self.amount:
                self.initialize()

    def optimal_stopping(self):
        action = self.trader.config.get(constants.ACTION)
        bitcoin_price = self.trader.bitcoin_quote.get(constants.PRICE)

        if self.trader.cycle_start_time < self.switch_time:
            self.trader.fetch_bitcoin_quote()

            if self.compare_price():
                self.set_price_to_beat()
            else:
                log.debug("LOOKING:")
                log.debug(f"\tCurrent price: {bitcoin_price}")
                log.debug(f"\tPrice to beat: {self.price_to_beat}")

        else:
            if self.price_to_beat:
                self.trader.fetch_bitcoin_quote()

                log.debug("READY TO LEAP:")
                log.debug(f"\tCurrent price: {bitcoin_price}")
                log.debug(f"\tPrice to beat: {self.price_to_beat}")

                if self.compare_price():
                    if action == constants.BUY:
                        bitcoin_amount = self.create_bitcoin_amount()
                    else:
                        bitcoin_amount = self.amount

                    log.info(
                        f"Placing order to {action} {bitcoin_amount:.8f} BTC at {(bitcoin_price):.2f} USD"
                    )

                    order = self.trader.gemini.new_order(
                        amount=str(bitcoin_amount),
                        price=str(bitcoin_price),
                        side=action.lower(),
                    )

                    log.debug(f"Created new order: {order.json()}")

                    self.initialize()

            if self.trader.cycle_start_time > self.end_time:
                self.initialize()

    def set_price_to_beat(self):
        max_price = self.trader.config.get(
            constants.MAX_PRICE, 1000 * 1000 * 1000
        )
        min_price = self.trader.config.get(constants.MIN_PRICE, 0)
        bitcoin_price = self.trader.bitcoin_quote.get(constants.PRICE)

        self.price_to_beat = min(max(bitcoin_price, min_price), max_price)

        log.info(f"Set new price to beat = {self.price_to_beat}")

    def set_start_time(self):
        if self.end_time:
            self.start_time = self.end_time
        else:
            self.start_time = self.trader.cycle_start_time

        log.info(f"Set start time = {self.start_time}")

    def set_switch_time(self):
        period = self.trader.config.get(constants.PERIOD)
        self.switch_time = self.start_time + period * STOPPING_FACTOR
        log.info(f"Set switch time = {self.switch_time}")

    def set_end_time(self):
        period = self.trader.config.get(constants.PERIOD)
        self.end_time = self.start_time + period
        log.info(f"Set end time = {self.end_time}")

    def calculate_amount(self):
        self.trader.fetch_account_balances()

        action = self.trader.config.get(constants.ACTION)
        amount = float(self.trader.config.get(constants.AMOUNT))
        stop_amount = float(self.trader.config.get(constants.STOP))
        usd_balance = self.trader.account_balances.get(constants.USD, 0)
        btc_balance = self.trader.account_balances.get(constants.BTC, 0)

        if action == constants.BUY:
            balance = usd_balance
        else:
            balance = btc_balance

        if stop_amount >= balance:
            self.amount = 0
        else:
            self.amount = min(amount, balance - stop_amount)

        if action == constants.BUY:
            log.info(f"Set amount to buy = {self.amount} {constants.USD}")
        else:
            log.info(f"Set amount to sell = {self.amount} {constants.BTC}")

    def compare_price(self):
        bitcoin_price = self.trader.bitcoin_quote.get(constants.PRICE)
        action = self.trader.config.get(constants.ACTION)
        if action == constants.BUY:
            return bitcoin_price < self.price_to_beat

        else:
            return bitcoin_price > self.price_to_beat

    def create_bitcoin_amount(self):
        bitcoin_price = self.trader.bitcoin_quote.get(constants.PRICE)
        return round((self.amount / bitcoin_price), 8)

