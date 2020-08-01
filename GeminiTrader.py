# built-in
import time
from logging import getLogger

# downloaded
from geminipy import Geminipy

# package
from ConfigMixin import ConfigMixin
from OptimalStopping import OptimalStopping

log = getLogger("gemini-trader")


class GeminiTrader(ConfigMixin, OptimalStopping):
    def __init__(self):
        self.API_KEY = "account-uEHKoKpC6pP18v7vsBk3"
        self.SECRET_KEY = "3zHhV3RFEUh9icTaeBSi4dRNfR1U"
        self.CONFIG_FILE = "config.ini"
        self.gemini = None
        self.config = {
            "action": None,
            "stop": None,
            "strategy": None,
            "period": None,
            "amount": None,
        }
        self.account_balances = dict()

        OptimalStopping.__init__(self)

    def run(self):
        self.login()

        while True:
            self.update_account_balances()
            self.update_configuration()
            self.run_strategy()

            time.sleep(5)

    def login(self):
        self.gemini = Geminipy(self.API_KEY, self.SECRET_KEY, live=True)
        log.debug(f"Logged in to gemini at url={self.gemini.base_url}")

    def update_account_balances(self):
        account_balances = self.gemini.balances().json()

        for balance in account_balances:
            currency = balance.get("currency")
            amount = float(balance.get("available"))
            self.account_balances.update({currency: amount})

        log.debug(f"Updated account balances: {self.account_balances} USD")

    def run_strategy(self):
        if self.config.get("strategy") == "OPTIMAL_STOPPING":
            self.optimal_stopping()

