# built-in
import time
import requests
from datetime import datetime
from logging import getLogger

# downloaded
from geminipy import Geminipy

# package
from Configuration import Configuration, STRATEGY
from Strategy import Strategy
from OptimalStopping import OptimalStopping

log = getLogger("gemini-trader")


class GeminiTrader(Configuration):
    def __init__(self):
        self.API_KEY = "account-uEHKoKpC6pP18v7vsBk3"
        self.SECRET_KEY = "3zHhV3RFEUh9icTaeBSi4dRNfR1U"
        self.CONFIG_FILE = "config.ini"
        self.RESOLUTION = 360
        self.gemini = None
        self.config = {
            "action": None,
            "stop": None,
            "strategy": None,
            "period": None,
            "amount": None,
        }
        self.strategy = None
        self.account_balances = dict()
        self.bitcoin_quote = {
            "ask": 0,
            "bid": 0,
        }
        self.current_time = datetime.now()

    def run(self):
        self.login()

        while True:
            self.update_current_time()
            self.update_account_balances()
            self.update_bitcoin_quote()
            self.update_configuration()
            self.implement_changes()

            if not self.strategy:
                self.create_strategy()

            self.run_strategy_or_retry_connection()

    def login(self):
        self.gemini = Geminipy(self.API_KEY, self.SECRET_KEY, live=True)
        log.debug(f"Logged in to gemini at url={self.gemini.base_url}")

    def update_current_time(self):
        self.current_time = datetime.now()

    def update_account_balances(self):
        account_balances = self.gemini.balances().json()

        for balance in account_balances:
            currency = balance.get("currency")
            amount = float(balance.get("available"))
            self.account_balances.update({currency: amount})

        log.debug(f"Updated account balances: {self.account_balances} USD")

    def update_bitcoin_quote(self):
        bitcoin_quote = self.gemini.pubticker().json()
        self.bitcoin_quote.update(
            {"ask": float(bitcoin_quote.get("ask", None))}
        )
        self.bitcoin_quote.update(
            {"bid": float(bitcoin_quote.get("bid", None))}
        )

        log.debug(f"Updated bitcoin quote: {self.bitcoin_quote}")

    def implement_changes(self):
        if STRATEGY in self.changes:
            self.reset_strategy()
        else:
            self.strategy.update()

    def create_strategy(self):
        strategy = self.config.get("strategy")
        if strategy == OptimalStopping.name:
            self.strategy = OptimalStopping(self)

        elif strategy is None:
            log.info("No strategy selected. No strategy will be run.")

        else:
            log.warn(f"Invalid strategy: {strategy}. No strategy will be run.")

        if self.strategy:
            log.info(f"Created strategy object {self.strategy}")

    def run_strategy_or_retry_connection(self):
        if isinstance(self.strategy, Strategy):
            try:
                self.strategy.run()

            except requests.exceptions.ConnectionError:
                log.error(
                    f"Connection failed. Retrying in {self.retry_time}s..."
                )
                time.sleep(self.retry_time)
                self.backoff_retry_time()

            else:
                self.reset_retry_time()
                time.sleep(self.calculate_cycle_time())

    def reset_strategy(self):
        self.strategy = None
        log.debug("Reset strategy.")

    def backoff_retry_time(self):
        self.retry_time *= 2
        if self.retry_time > 128:
            self.retry_time = 2

    def reset_retry_time(self):
        self.retry_time = 2

    def calculate_cycle_time(self):
        return self.config.get("period").total_seconds() / self.RESOLUTION

