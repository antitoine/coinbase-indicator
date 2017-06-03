# Need package python-gi

import signal
from indicator.indicator import Indicator
from indicator.coinbase import Coinbase

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    client = Coinbase()
    app = Indicator(client)
    app.run()
