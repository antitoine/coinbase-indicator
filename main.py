# Need package python-gi

from __future__ import print_function
import sys
import signal
from os.path import join
from os import getcwd
from threading import Timer
import webbrowser
import json
import requests
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify


APPINDICATOR_ID = 'coinbase_indicator'

ICON_INACTIVE = 'icon-0'
ICON_ACTIVE = 'icon-1'

BITCOIN_KEY = 'BTC'
ETHEREUM_KEY = 'ETH'
LITCOIN_KEY = 'LTC'

FINAL_CURRENCY = 'EUR'

COINBASE_API_URL = 'https://api.coinbase.com/'
COINBASE_URL = 'https://www.coinbase.com/'
COINBASE_API_VERSION = 'v2'
COINBASE_API_VERSION_DATE = '2017-06-03'

MENU_ITEM_PRICE = 'Price-'
MENU_ITEM_REFRESH = 'Refresh'
MENU_ITEM_QUIT = 'Quit'

class CoinbaseAppIndicator(object):

    def __init__(self):
        notify.init(APPINDICATOR_ID)
        self.indicator = appindicator.Indicator.new(
            APPINDICATOR_ID, self.__icon_path(ICON_INACTIVE), appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.alarm = False
        self.prices = {
            BITCOIN_KEY: '-1',
            ETHEREUM_KEY: '-1',
            LITCOIN_KEY: '-1',
        }
        self.__init_menu()
        self.update()

    def run(self):
        self.__display_notification('Indicator started')
        gtk.main()

    def update(self):
        self.__update_prices()
        self.__update_icon()
        self.__update_menu()

    def quit(self, _):
        notify.uninit()
        gtk.main_quit()

    def goto_coinbase(self, _):
        webbrowser.open(COINBASE_URL)

    def refresh(self, _):
        # self.__disable_menu_item(MENU_ITEM_REFRESH)
        self.update()
        notification_msg = 'Prices updated<br>'
        for crypto_currency in self.prices:
            notification_msg += '1 ' + crypto_currency + ' = ' + self.prices[crypto_currency] + '<br>'
        self.__display_notification(notification_msg)
        # Timer(5.0, lambda: self.__enable_menu_item(MENU_ITEM_REFRESH))

    def __update_prices(self):
        for crypto_currency in self.prices:
            self.prices[crypto_currency] = self.__coinbase_get_spot_price(crypto_currency)

    def __update_icon(self):
        if self.alarm:
            self.indicator.set_icon(self.__icon_path(ICON_ACTIVE))
        else:
            self.indicator.set_icon(self.__icon_path(ICON_INACTIVE))

    def __init_menu(self):
        self.menu = gtk.Menu()

        self.menu_items = {}
        for crypto_currency in self.prices:
            item = gtk.MenuItem(self.__get_price_menu_label(crypto_currency))
            item.connect('activate', self.goto_coinbase)
            self.menu_items[MENU_ITEM_PRICE + crypto_currency] = item
            self.menu.append(item)

        self.menu.append(gtk.SeparatorMenuItem("Options"))

        item_refresh = gtk.MenuItem(MENU_ITEM_REFRESH)
        item_refresh.connect('activate', self.refresh)
        self.menu_items[MENU_ITEM_REFRESH] = item_refresh
        self.menu.append(item_refresh)

        item_quit = gtk.MenuItem(MENU_ITEM_QUIT)
        item_quit.connect('activate', self.quit)
        self.menu_items[MENU_ITEM_QUIT] = item_quit
        self.menu.append(item_quit)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

    def __update_menu(self):
        for crypto_currency in self.prices:
            self.menu_items[MENU_ITEM_PRICE + crypto_currency].get_child().set_text(self.__get_price_menu_label(crypto_currency))

    def __get_price_menu_label(self, crypto_currency):
        return '1 ' + crypto_currency + ' = ' + str(self.prices[crypto_currency])

    def __coinbase_get_spot_price(self, crypto_currency):
        data = self.__coinbase_get('prices/' + crypto_currency + '-' + FINAL_CURRENCY + '/spot')
        if 'amount' in data:
            amount = data['amount']
            currency = ''
            if 'currency' in data:
                if data['currency'] == 'EUR':
                    currency = '€'
                elif data['currency'] == 'USD':
                    currency = '$'
            return str(amount) + ' ' + currency
        else:
            return -1

    def __coinbase_get(self, uri):
        response = requests.get(
            COINBASE_API_URL + COINBASE_API_VERSION + '/' + uri,
            headers={
                'content-type': 'application/json',
                'CB-VERSION': COINBASE_API_VERSION_DATE,
            },
        )
        json_data = json.loads(response.text)
        if 'warnings' in json_data:
            for warning in json_data['warnings']:
                print('Warning - '
                      + (warning['message'] if 'message' in warning else '')
                      + (' - ' + warning['id'] if 'id' in warning else '')
                      + (' - ' + warning['url'] if 'url' in warning else ''), file=sys.stderr)
        if 'errors' in json_data:
            for error in json_data['errors']:
                print('Error - '
                      + (error['message'] if 'message' in error else '')
                      + (' - ' + error['id'] if 'id' in error else '')
                      + (' - ' + error['url'] if 'url' in error else ''), file=sys.stderr)
        if 'data' in json_data:
            return json_data['data']
        else:
            return json_data

    def __icon_path(self, name):
        return join(getcwd(), 'img', '%s.svg' % name)

    def __display_notification(self, msg):
        notify.Notification.new('<b>Coinbase Indicator</b>', msg, self.__icon_path(ICON_ACTIVE),).show()

    def __disable_menu_item(self, item_name):
        self.menu_items[item_name].set_sensitive(False)
        self.menu_items[item_name].show()

    def __enable_menu_item(self, item_name):
        self.menu_items[item_name].set_sensitive(True)
        self.menu_items[item_name].show()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    CoinbaseAppIndicator().run()
