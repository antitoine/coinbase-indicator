class Backend(object):

    def get_available_real_currencies(self):
        raise NotImplementedError("Must define get_available_real_currencies to use this base class")

    def set_real_currency(self, real_currency):
        raise NotImplementedError("Must define set_real_currency to use this base class")

    def get_real_currency(self):
        raise NotImplementedError("Must define get_real_currency to use this base class")

    def get_available_crypto_currencies(self):
        raise NotImplementedError("Must define available_crypto_currencies to use this base class")

    def get_spot_price(self, crypto_currency):
        raise NotImplementedError("Must define get_spot_price to use this base class")

    def get_store_url(self):
        raise NotImplementedError("Must define get_store_url to use this base class")
