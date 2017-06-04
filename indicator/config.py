import os
import json
import re

CONFIG_FILE_PATH = os.path.expanduser("~/.coinbase-indicator")

OPTION_KEY_NOTIFICATION = 'show_notifications'
OPTION_KEY_THEME_MONOCHROME = 'theme_monochrome'
OPTION_KEY_CRYPTO_CURRENCY = 'show_crypto_currency_'


class Option(object):
    def __init__(self, status, label, crypto_currency=None):
        self.status = status
        self.label = label
        self.crypto_currency = crypto_currency

    def get_label(self):
        return self.label

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def is_crypto_currency_option(self):
        return self.crypto_currency is not None

    def get_crypto_currency(self):
        return self.crypto_currency


class Config(object):

    def __init__(self):
        self.options = {
            OPTION_KEY_NOTIFICATION: Option(True, self.__get_label(OPTION_KEY_NOTIFICATION)),
            OPTION_KEY_THEME_MONOCHROME: Option(True, self.__get_label(OPTION_KEY_THEME_MONOCHROME)),
        }

    def has_crypto_currency_option(self, crypto_currency):
        return OPTION_KEY_CRYPTO_CURRENCY + crypto_currency in self.options

    def get_crypto_currency_option(self, crypto_currency):
        return self.options[OPTION_KEY_CRYPTO_CURRENCY + crypto_currency]

    def get_notification_option(self):
        return self.options[OPTION_KEY_NOTIFICATION]

    def get_theme_monochrome_option(self):
        return self.options[OPTION_KEY_THEME_MONOCHROME]

    def has_option(self, key):
        return key in self.options

    def get_option(self, key):
        return self.options[key]

    def get_options(self):
        return self.options

    def set_crypto_currencies_options(self, crypto_currencies):
        for crypto_currency in crypto_currencies:
            if OPTION_KEY_CRYPTO_CURRENCY + crypto_currency not in self.options:
                self.options[OPTION_KEY_CRYPTO_CURRENCY + crypto_currency] = Option(False, self.__get_label(OPTION_KEY_CRYPTO_CURRENCY + crypto_currency), crypto_currency)

    def load(self):
        if not os.path.isfile(CONFIG_FILE_PATH):
            return
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            config_dict = json.load(config_file)
        for config_key in config_dict:
            self.options[config_key] = Option(config_dict.get(config_key), self.__get_label(config_key), self.__find_crypto_currency(config_key))

    def persist(self):
        config_dict = {}
        for config_key in self.options:
            config_dict[config_key] = self.options[config_key].get_status()
        with open(CONFIG_FILE_PATH, 'w') as config_file:
            json.dump(config_dict, config_file)

    @staticmethod
    def __find_crypto_currency(key):
        crypto_currency_math = re.search(r'^' + OPTION_KEY_CRYPTO_CURRENCY + '([A-Z]+)$', key)
        if crypto_currency_math:
            return crypto_currency_math.group(1)
        else:
            return None

    @staticmethod
    def __get_label(key):
        label = key.replace('_', ' ')
        return label[:1].upper() + label[1:]
