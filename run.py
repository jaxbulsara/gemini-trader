# built-in
import sys
from datetime import datetime

# package
from setup_logging import setup_logging

if __name__ == "__main__":
    try:
        debug_mode = sys.argv[1]
    except IndexError:
        debug_mode = False

    setup_logging(debug=debug_mode)

    from GeminiTrader import GeminiTrader

    trader = GeminiTrader()
    trader.run()
