import os
import json

CONFIG_FILE_PATH = os.path.expanduser("~/.coinbase-indicator")

GENERAL_OPTION_KEY = 'general'
OPTION_KEY_LARGE_LABEL = 'show_crypto_currency_in_the_label'
OPTION_KEY_NOTIFICATION = 'show_notifications'
OPTION_KEY_THEME_MONOCHROME = 'theme_monochrome'

CRYPTO_CURRENCY_OPTION_KEY = 'crypto_currency'
OPTION_KEY_CRYPTO_CURRENCY_SHOW = 'show_exchange_price'


class Option(object):
    def __init__(self, status, label):
        self.status = status
        self.label = label

    def get_label(self):
        return self.label

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status


class Config(object):

    def __init__(self):
        self.general_options = {
            OPTION_KEY_LARGE_LABEL: Option(False, self.__get_label(OPTION_KEY_LARGE_LABEL)),
            OPTION_KEY_NOTIFICATION: Option(True, self.__get_label(OPTION_KEY_NOTIFICATION)),
            OPTION_KEY_THEME_MONOCHROME: Option(True, self.__get_label(OPTION_KEY_THEME_MONOCHROME)),
        }
        self.crypto_currency_options = {}

    def set_crypto_currencies_options(self, crypto_currencies):
        for crypto_currency in crypto_currencies:
            if crypto_currency not in self.crypto_currency_options:
                self.crypto_currency_options[crypto_currency] = {
                    OPTION_KEY_CRYPTO_CURRENCY_SHOW: Option(False, self.__get_label(OPTION_KEY_CRYPTO_CURRENCY_SHOW)),
                }

    def load(self):
        if not os.path.isfile(CONFIG_FILE_PATH):
            return
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            config_dict = json.load(config_file)

        if GENERAL_OPTION_KEY in config_dict:
            for option_key in config_dict[GENERAL_OPTION_KEY]:
                self.general_options[option_key] = Option(config_dict[GENERAL_OPTION_KEY][option_key], self.__get_label(option_key))

        if CRYPTO_CURRENCY_OPTION_KEY in config_dict:
            for crypto_currency in config_dict[CRYPTO_CURRENCY_OPTION_KEY]:
                if crypto_currency not in self.crypto_currency_options:
                    self.crypto_currency_options[crypto_currency] = {}
                for option_key in config_dict[CRYPTO_CURRENCY_OPTION_KEY][crypto_currency]:
                    self.crypto_currency_options[crypto_currency][option_key] = Option(config_dict[CRYPTO_CURRENCY_OPTION_KEY][crypto_currency][option_key], self.__get_label(option_key))

    def persist(self):
        config_dict = {
            GENERAL_OPTION_KEY: {},
            CRYPTO_CURRENCY_OPTION_KEY: {},
        }

        for option_key in self.general_options:
            config_dict[GENERAL_OPTION_KEY][option_key] = self.general_options[option_key].get_status()

        for crypto_currency in self.crypto_currency_options:
            config_dict[CRYPTO_CURRENCY_OPTION_KEY][crypto_currency] = {}
            for option_key in self.crypto_currency_options[crypto_currency]:
                config_dict[CRYPTO_CURRENCY_OPTION_KEY][crypto_currency][option_key] = self.crypto_currency_options[crypto_currency][option_key].get_status()

        with open(CONFIG_FILE_PATH, 'w') as config_file:
            json.dump(config_dict, config_file)

    def get_crypto_currency_options(self):
        return self.crypto_currency_options

    def get_general_options(self):
        return self.general_options

    def is_crypto_currency_visible(self, crypto_currency):
        return \
            crypto_currency in self.crypto_currency_options \
            and OPTION_KEY_CRYPTO_CURRENCY_SHOW in self.crypto_currency_options[crypto_currency] \
            and self.crypto_currency_options[crypto_currency][OPTION_KEY_CRYPTO_CURRENCY_SHOW].get_status()

    def is_theme_monochrome(self):
        return \
            OPTION_KEY_THEME_MONOCHROME in self.general_options \
            and self.general_options[OPTION_KEY_THEME_MONOCHROME].get_status()

    def is_notification_visible(self):
        return \
            OPTION_KEY_NOTIFICATION in self.general_options \
            and self.general_options[OPTION_KEY_NOTIFICATION].get_status()

    def is_large_label_visible(self):
        return \
            OPTION_KEY_LARGE_LABEL in self.general_options \
            and self.general_options[OPTION_KEY_LARGE_LABEL].get_status()


    @staticmethod
    def __get_label(key):
        label = key.replace('_', ' ')
        return label[:1].upper() + label[1:]
