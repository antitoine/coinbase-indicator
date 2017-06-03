from os.path import join
from os import getcwd
import webbrowser
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

MENU_ITEM_PRICE = 'Price-'
MENU_ITEM_REFRESH = 'Refresh'
MENU_ITEM_QUIT = 'Quit'

ICON_INACTIVE = 'icon-0'
ICON_ACTIVE = 'icon-1'


class Ui(object):

    def __init__(self, app_id, crypto_currencies, real_currency, store_url, refresh_fc, quit_fc):
        self.real_currency_label = ''
        self.store_url = ''
        self.indicator = None

        self.indicator = appindicator.Indicator.new(app_id, self.__icon_path(ICON_INACTIVE), appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        notify.init(app_id)
        self.change_real_currency(real_currency)
        self.store_url = store_url
        self.__init_menu(crypto_currencies, refresh_fc, quit_fc)

    def set_active(self):
        self.indicator.set_icon(self.__icon_path(ICON_ACTIVE))

    def set_inactive(self):
        self.indicator.set_icon(self.__icon_path(ICON_INACTIVE))

    def update_prices(self, crypto_currencies):
        for crypto_currency in crypto_currencies:
            self.menu_items[MENU_ITEM_PRICE + crypto_currency].get_child().set_text(
                self.__get_exchange_price_label(crypto_currency, crypto_currencies[crypto_currency])
            )
            self.menu_items[MENU_ITEM_PRICE + crypto_currency].show()

    def change_real_currency(self, real_currency):
        if real_currency == 'EUR':
            # Euro symbol
            self.real_currency_label = u'\u20AC'
        elif real_currency == 'USD':
            # Dollar symbol
            self.real_currency_label = u'\u0024'
        else:
            self.real_currency_label = real_currency

    def disable_menu_item(self, item_name):
        self.menu_items[item_name].set_sensitive(False)
        self.menu_items[item_name].show()

    def enable_menu_item(self, item_name):
        self.menu_items[item_name].set_sensitive(True)
        self.menu_items[item_name].show()

    def display_notification(self, msg):
        notify.Notification.new('<b>Coinbase Indicator</b>', msg, self.__icon_path(ICON_ACTIVE),).show()

    def display(self):
        gtk.main()

    def close(self):
        notify.uninit()
        gtk.main_quit()

    def __init_menu(self, crypto_currencies, refresh_fc, quit_fc):
        self.menu = gtk.Menu()

        self.menu_items = {}
        for crypto_currency in crypto_currencies:
            item = gtk.MenuItem(self.__get_exchange_price_label(crypto_currency, crypto_currencies[crypto_currency]))
            item.connect('activate', self.__open_store)
            self.menu_items[MENU_ITEM_PRICE + crypto_currency] = item
            self.menu.append(item)

        self.menu.append(gtk.SeparatorMenuItem("Options"))

        item_refresh = gtk.MenuItem(MENU_ITEM_REFRESH)
        item_refresh.connect('activate', lambda _: refresh_fc())
        self.menu_items[MENU_ITEM_REFRESH] = item_refresh
        self.menu.append(item_refresh)

        item_quit = gtk.MenuItem(MENU_ITEM_QUIT)
        item_quit.connect('activate', lambda _: quit_fc())
        self.menu_items[MENU_ITEM_QUIT] = item_quit
        self.menu.append(item_quit)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

    def __get_exchange_price_label(self, crypto_currency, price):
        return '1 ' + crypto_currency + ' = ' + str(price) + self.real_currency_label

    @staticmethod
    def __icon_path(name):
        return join(getcwd(), 'img', '%s.svg' % name)

    def __open_store(self, _):
        webbrowser.open(self.store_url)
