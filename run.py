# built-in
from datetime import datetime

# package
from setup_logging import setup_logging

if __name__ == "__main__":
    start_datetime = datetime.now().strftime("%Y-%m-%S_%H-%M-%S-%f")
    setup_logging(start_datetime, debug=True, file=False)

    from GeminiTrader import GeminiTrader

    trader = GeminiTrader()
    trader.run()
