# built-in
from datetime import datetime

# package
from setup_logging import setup_logging

if __name__ == "__main__":
    start_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    setup_logging(start_datetime)

    from GeminiTrader import GeminiTrader

    trader = GeminiTrader()
    trader.run()
