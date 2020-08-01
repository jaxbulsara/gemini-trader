# built-in
import re
from configparser import ConfigParser
from datetime import timedelta
from logging import getLogger

# package
from GeminiTrader import GeminiTrader

log = getLogger("gemini-trader")


class ConfigMixin:
    self: GeminiTrader

    def update_configuration(self):
        def update_action():
            action = config.get("action", None)

            if self.config.get("action") != action:
                self.config.update({"action": action})
                log.info(f"Changed action to {action}")

        def update_stop():
            stop = config.get("stop", None)

            if self.config.get("stop") != stop:
                self.config.update({"stop": stop})
                log.info(f"Changed stop value to {stop}")

        def update_strategy():
            strategy = config.get("strategy", None)

            if self.config.get("strategy") != strategy:
                self.config.update({"strategy": strategy})
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

            period = parse(config.get("period", None))

            if self.config.get("period") != period:
                self.config.update({"period": period})
                log.info(f"Changed stategy period to {period}")

        def update_amount():
            amount = config.get("amount", None)

            if self.config.get("amount") != amount:
                self.config.update({"amount": amount})
                log.info(f"Changed amount to {amount}")

        config = ConfigParser()
        config.read(self.CONFIG_FILE)
        config = config["gemini-trader"]

        log.debug(f"Current configuration: {self.config}")

        update_action()
        update_stop()
        update_strategy()
        update_period()
        update_amount()
