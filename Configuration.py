# built-in
import re
from configparser import ConfigParser
from datetime import timedelta
from logging import getLogger

ACTION = "action"
BUY = "BUY"
SELL = "SELL"
STOP = "stop"
STRATEGY = "strategy"
PERIOD = "period"
AMOUNT = "amount"
USD = "USD"
BTC = "BTC"

log = getLogger("gemini-trader")


class Configuration:
    def update_configuration(self):
        def update_action():
            action = config.get(ACTION, None)

            if self.config.get(ACTION) != action:
                self.changes.append(ACTION)
                self.config.update({ACTION: action})
                log.info(f"Changed action to {action}")

        def update_stop():
            stop = config.get(STOP, None)

            if self.config.get(STOP) != stop:
                self.changes.append(STOP)
                self.config.update({STOP: stop})
                log.info(f"Changed stop value to {stop}")

        def update_strategy():
            strategy = config.get(STRATEGY, None)

            if self.config.get(STRATEGY) != strategy:
                self.changes.append(STRATEGY)
                self.config.update({STRATEGY: strategy})
                log.info(f"Changed strategy to {strategy}")

        def update_period():
            def parse(period_config):
                DEFAULT = timedelta(hours=1)
                MINIMUM = timedelta(seconds=30)

                def default():
                    log.warn(
                        f"Invalid configuration parameter: Period - '{period_config}'. Using default period - {DEFAULT}"
                    )
                    return DEFAULT

                def minimum():
                    log.warn(
                        f"Period cannot be less than 30s. Using minimum period - {MINIMUM}."
                    )
                    return MINIMUM

                def get_parts():
                    pattern = r"((?P<weeks>\d+?)W)?((?P<days>\d+?)D)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?"
                    expression = re.compile(pattern)
                    return expression.match(period_config)

                def create_time_parameters(parts):
                    parts = parts.groupdict()
                    time_parameters = {"days": 0, "minutes": 0, "seconds": 0}
                    log.debug(f"Period time parameters = {parts}")

                    for (name, _) in parts.items():
                        if name == "weeks":
                            time_parameters["days"] += (
                                float(parts.get(name) or 0) * 7
                            )

                        elif name == "days":
                            time_parameters["days"] += float(
                                parts.get(name) or 0
                            )

                        elif name == "hours":
                            time_parameters["minutes"] += (
                                float(parts.get(name) or 0) * 60
                            )

                        elif name == "minutes":
                            time_parameters["minutes"] += float(
                                parts.get(name) or 0
                            )

                        elif name == "seconds":
                            time_parameters["seconds"] += float(
                                parts.get(name) or 0
                            )

                    return time_parameters

                parts = get_parts()

                if not parts:
                    return default()

                time_parameters = create_time_parameters(parts)
                period = timedelta(**time_parameters)

                if period == timedelta():
                    return default()

                if period < MINIMUM:
                    return minimum()

                return period

            period = parse(config.get(PERIOD, None))

            if self.config.get(PERIOD) != period:
                self.changes.append(PERIOD)
                self.config.update({PERIOD: period})
                log.info(f"Changed stategy period to {period}")

        def update_amount():
            amount = config.get(AMOUNT, None)

            if self.config.get(AMOUNT) != amount:
                self.changes.append(AMOUNT)
                self.config.update({AMOUNT: amount})
                log.info(f"Changed amount to {amount}")

        config = ConfigParser()
        config.read(self.CONFIG_FILE)
        config = config["gemini-trader"]

        log.debug(f"Current configuration: {self.config}")

        self.changes = []
        update_action()
        update_stop()
        update_strategy()
        update_period()
        update_amount()
