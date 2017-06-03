from .ui import Ui
from .backend import Backend
from threading import Timer

APPINDICATOR_ID = 'coinbase_indicator'


class Indicator(object):

    def __init__(self, client):
        self.client = client

        self.prices = {}
        self.__update_prices()

        # TODO make this changeable
        self.real_currency = 'EUR'

        self.interface = Ui(
            APPINDICATOR_ID,
            self.prices,
            self.client.get_real_currency(),
            self.client.get_store_url(),
            self.__refresh,
            self.__quit
        )

        self.refresh_thread = None

    def run(self):
        self.__repeat_update()
        self.interface.display()

    def __repeat_update(self):
        self.__refresh(True)
        # TODO make the update time changeable
        self.refresh_thread = Timer(30.0, self.__repeat_update)
        self.refresh_thread.start()

    def __update_prices(self):
        for crypto_currency in self.client.get_available_crypto_currencies():
            self.prices[crypto_currency] = self.client.get_spot_price(crypto_currency)

    def __refresh(self, silent=False):
        self.__update_prices()
        self.interface.update_prices(self.prices)
        if not silent:
            self.interface.display_notification('Prices updated')

    def __quit(self):
        self.refresh_thread.cancel()
        self.interface.close()

