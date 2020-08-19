# built-in
import time
import requests
import json
from statistics import mean
from datetime import datetime, timedelta
from logging import getLogger

# downloaded
from geminipy import Geminipy

# package
import constants
from strategies import Strategy, STRATEGIES

log = getLogger("gemini-trader")


class GeminiTrader:
    def __init__(self):
        self.gemini = None
        self.config = None
        self.strategy = None
        self.account_balances = dict()
        self.bitcoin_quote = dict()
        self.cycle_start_time = None
        self.retry_time = 2

    def run(self):
        self.login()
        self.setup()

        while True:
            try:
                self.set_cycle_start_time()
                self.strategy.run()

            except requests.exceptions.ConnectionError:
                log.error(
                    f"Connection failed. Retrying in {self.retry_time}s..."
                )
                time.sleep(self.retry_time)
                self.backoff_retry_time()

            else:
                self.reset_retry_time()
                time.sleep(self.calculate_wait_time())

    def login(self):
        with open(constants.KEYS_FILE, "r") as keys_file:
            keys_json = json.load(keys_file)
            keys = (keys_json["api_key"], keys_json["secret_key"])

        while not self.gemini:
            try:
                self.gemini = Geminipy(*keys, live=True)

            except requests.exceptions.ConnectionError:
                log.error(
                    f"Connection failed. Retrying in {self.retry_time}s..."
                )
                time.sleep(self.retry_time)
                self.backoff_retry_time()

            else:
                self.reset_retry_time()
                log.debug(f"Logged in to gemini at url={self.gemini.base_url}")
                # log.debug(f"{self.gemini.api_key=}")
                # log.debug(f"{self.gemini.secret_key=}")

    def setup(self):
        while True:
            try:
                self.read_configuration()
                self.fetch_account_balances()
                self.fetch_bitcoin_quote()
                self.create_strategy()
                break

            except requests.exceptions.ConnectionError:
                log.error(
                    f"Connection failed. Retrying in {self.retry_time}s..."
                )
                time.sleep(self.retry_time)
                self.backoff_retry_time()

            else:
                self.reset_retry_time()

    def read_configuration(self):
        def convert_period():
            self.config[constants.PERIOD] = timedelta(
                seconds=self.config.get(constants.PERIOD)
            )

        def validate_configuration():
            if constants.ACTION not in self.config.keys():
                raise AttributeError(
                    f"Configuration must contain a value for '{constants.ACTION}'."
                )

            if constants.STRATEGY not in self.config.keys():
                raise AttributeError(
                    f"Configuration must contain a value for '{constants.STRATEGY}'."
                )

            if constants.PERIOD not in self.config.keys():
                raise AttributeError(
                    f"Configuration must contain a value for '{constants.PERIOD}'."
                )

            if constants.CYCLE_TIME not in self.config.keys():
                raise AttributeError(
                    f"Configuration must contain a value for '{constants.CYCLE_TIME}'."
                )

            if constants.AMOUNT not in self.config.keys():
                raise AttributeError(
                    f"Configuration must contain a value for '{constants.AMOUNT}'."
                )

            if constants.STOP not in self.config.keys():
                raise AttributeError(
                    f"Configuration must contain a value for '{constants.STOP}'."
                )

            if self.config.get(constants.ACTION) not in constants.ACTIONS:
                raise ValueError(f"Action must be one of {constants.ACTIONS}")

            if self.config.get(constants.STRATEGY) not in STRATEGIES:
                raise ValueError(
                    f"Strategy must be one of {set(STRATEGIES.keys())}"
                )

            if type(self.config.get(constants.PERIOD)) not in [int, float]:
                raise TypeError(
                    f"Period must be a value in seconds. Got {type(self.config.get(constants.PERIOD))}."
                )

            if type(self.config.get(constants.CYCLE_TIME)) not in [int, float]:
                raise TypeError(
                    f"Cycle time must be a value in seconds. Got {type(self.config.get(constants.CYCLE_TIME))}."
                )

            if type(self.config.get(constants.AMOUNT)) not in [int, float]:
                raise TypeError(
                    f"Amount to buy must be a value in USD or BTC. Got {type(self.config.get(constants.AMOUNT, None))}."
                )

            if type(self.config.get(constants.STOP)) not in [int, float]:
                raise TypeError(
                    f"Stop amount must be a value in USD or BTC. Got {type(self.config.get(constants.STOP, None))}."
                )

        with open(constants.CONFIG_FILE, "r") as config_file:
            self.config = json.load(config_file)

        validate_configuration()
        convert_period()

        log.debug(f"Configuration: {self.config}")

    def set_cycle_start_time(self):
        self.cycle_start_time = datetime.now()
        # log.debug(f"Updated cycle start time = {self.cycle_start_time}")

    def fetch_account_balances(self):
        account_balances = self.gemini.balances().json()

        for balance in account_balances:
            currency = balance.get("currency")
            amount = float(balance.get("available"))
            self.account_balances.update({currency: amount})

        log.debug(f"Updated account balances: {self.account_balances}")

    def fetch_bitcoin_quote(self):
        bitcoin_quote = self.gemini.pubticker().json()
        ask = float(bitcoin_quote.get(constants.ASK, 0))
        bid = float(bitcoin_quote.get(constants.BID, 0))
        self.bitcoin_quote.update(
            {
                constants.ASK: ask,
                constants.BID: bid,
                constants.PRICE: round((mean([ask, bid])), 2),
            }
        )

        log.debug(f"Updated bitcoin quote: {self.bitcoin_quote}")

    def create_strategy(self):
        self.strategy = STRATEGIES[self.config["strategy"]](self)
        log.info(f"Running strategy: {self.config['strategy']}")

    def backoff_retry_time(self):
        self.retry_time *= 2
        if self.retry_time > 300:
            self.retry_time = 2

    def reset_retry_time(self):
        self.retry_time = 2

    def calculate_wait_time(self):
        current_time = datetime.now()
        time_since_start = current_time - self.cycle_start_time

        return max(
            self.config.get(constants.CYCLE_TIME)
            - time_since_start.total_seconds(),
            0,
        )

