from logging import getLogger

log = getLogger("gemini-trader")

STRATEGIES = {}


def register_class(target_class):
    STRATEGIES[target_class.name] = target_class
    log.debug(f"Registering new strategy: {target_class.name}")


class StrategyRegistry(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        if name != "Strategy":
            if "name" not in class_dict.keys():
                raise NotImplementedError("Strategy must have a name.")

            if class_dict["name"] not in STRATEGIES:
                register_class(cls)

        return cls


class Strategy(metaclass=StrategyRegistry):
    def __init__(self, trader):
        self.trader = trader

    def initialize(self):
        raise NotImplementedError(
            "Strategy 'initialize' function must be defined."
        )

    def run(self):
        raise NotImplementedError("Strategy 'run' function must be defined.")

    def update(self):
        raise NotImplementedError("Strategy 'update' function must be defined.")
