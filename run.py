# built-in
from datetime import datetime

# package
from setup_logging import setup_logging

if __name__ == "__main__":
<<<<<<< Updated upstream
    start_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
=======
    start_datetime = datetime.now().strftime("%Y-%m-%S_%H-%M-%S-%f")
>>>>>>> Stashed changes
    setup_logging(start_datetime)

    from GeminiTrader import GeminiTrader

    trader = GeminiTrader()
    trader.run()
