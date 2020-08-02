class Strategy:
    name = None

    def __init__(self, trader):
        self.trader = trader

    @property
    def name(self):
        raise NotImplementedError("Strategy must have a name.")

    def initialize(self):
        raise NotImplementedError(
            "Strategy 'initialize' function must be defined."
        )

    def run(self):
        raise NotImplementedError("Strategy 'run' function must be defined.")

    def update(self):
        raise NotImplementedError("Strategy 'update' function must be defined.")
