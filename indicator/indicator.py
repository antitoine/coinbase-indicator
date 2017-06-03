from .ui import Ui
from .backend import Backend

APPINDICATOR_ID = 'coinbase_indicator'


class Indicator(object):

    def __init__(self, client: Backend):
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

    def run(self):
        self.interface.display()
        self.interface.display_notification('Indicator started')
        # TODO refresh every X seconds

    def __update_prices(self):
        for crypto_currency in self.client.get_available_crypto_currencies():
            self.prices[crypto_currency] = self.client.get_spot_price(crypto_currency)

    def __refresh(self):
        self.__update_prices()
        self.interface.update_prices(self.prices)
        self.interface.display_notification('Prices updated')

    def __quit(self):
        self.interface.close()
