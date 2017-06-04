from os.path import join
from os import path
import webbrowser
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

MENU_ITEM_PRICE = 'price_'
MENU_ITEM_REFRESH = 'refresh'
MENU_ITEM_SETTINGS = 'settings_'
MENU_ITEM_QUIT = 'quit'

ICON_MONOCHROME = 'icon-0'
ICON_COLOR = 'icon-1'


class Ui(object):

    def __init__(self, app_id, prices, real_currency, store_url, refresh_fc, quit_fc, config):
        self.real_currency_label = ''
        self.store_url = store_url
        self.config = config
        self.refresh_fc = refresh_fc
        self.quit_fc = quit_fc
        self.prices = prices

        self.indicator = appindicator.Indicator.new(app_id, self.__get_icon_path(), appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_label('', '')
        notify.init(app_id)

        self.change_real_currency(real_currency, self.prices)

    def update_prices(self, prices):
        self.prices = prices
        self.__update_menu()
        self.__update_indicator_label()

    def change_real_currency(self, real_currency, prices):
        if real_currency == 'EUR':
            # Euro symbol
            self.real_currency_label = u'\u20AC'
        elif real_currency == 'USD':
            # Dollar symbol
            self.real_currency_label = u'\u0024'
        else:
            self.real_currency_label = real_currency
        self.update_prices(prices)

    def display_notification(self, msg):
        if self.config.is_notification_visible():
            notify.Notification.new('<b>Coinbase Indicator</b>', msg, self.__get_icon_path(),).show()

    def display(self):
        gtk.main()

    def close(self):
        notify.uninit()
        gtk.main_quit()

    def __update_icon(self):
        self.indicator.set_icon(self.__get_icon_path())

    def __update_menu(self):
        menu = gtk.Menu()

        for crypto_currency in self.prices:
            item = gtk.MenuItem(self.__get_exchange_price_label(crypto_currency, self.prices[crypto_currency]))
            item.connect('activate', self.__open_store)
            menu.append(item)

        menu.append(gtk.SeparatorMenuItem())

        item_refresh = gtk.MenuItem('Refresh prices')
        item_refresh.connect('activate', lambda _: self.refresh_fc())
        menu.append(item_refresh)

        menu.append(gtk.SeparatorMenuItem())

        crypto_currency_options = self.config.get_crypto_currency_options()
        for crypto_currency in crypto_currency_options:
            crypto_currency_sub_menu = gtk.Menu()
            for option_key in crypto_currency_options[crypto_currency]:
                item = gtk.CheckMenuItem(crypto_currency_options[crypto_currency][option_key].get_label(), active=crypto_currency_options[crypto_currency][option_key].get_status())
                item.connect("activate", lambda _, currency, key: self.__toggle_crypto_currency_option_status(currency, key), crypto_currency, option_key)
                crypto_currency_sub_menu.append(item)
            crypto_currency_item = gtk.MenuItem(crypto_currency)
            crypto_currency_item.set_submenu(crypto_currency_sub_menu)
            menu.append(crypto_currency_item)

        menu.append(gtk.SeparatorMenuItem())

        general_settings_sub_menu = gtk.Menu()
        options = self.config.get_general_options()
        for option_key in options:
            item = gtk.CheckMenuItem(options[option_key].get_label(), active=options[option_key].get_status())
            item.connect("activate", lambda _, key: self.__toggle_general_option_status(key), option_key)
            general_settings_sub_menu.append(item)
        general_settings_item = gtk.MenuItem('Settings')
        general_settings_item.set_submenu(general_settings_sub_menu)
        menu.append(general_settings_item)

        menu.append(gtk.SeparatorMenuItem())

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', lambda _: self.quit_fc())
        menu.append(item_quit)

        menu.show_all()
        self.indicator.set_menu(menu)

    def __update_indicator_label(self):
        label = ''
        large = self.config.is_large_label_visible()
        for crypto_currency in self.prices:
            if self.config.is_crypto_currency_visible(crypto_currency):
                label += ' | ' + self.__get_exchange_price_label(crypto_currency, self.prices[crypto_currency], large)
        if label:
            label = label[2:]
        self.indicator.set_label(label, '')

    def __toggle_general_option_status(self, option_key):
        option = self.config.get_general_options()[option_key]
        option.set_status(not option.get_status())
        self.__update_indicator_label()
        self.__update_icon()
        self.__update_menu()
        self.config.persist()

    def __toggle_crypto_currency_option_status(self, crypto_currency, option_key):
        option = self.config.get_crypto_currency_options()[crypto_currency][option_key]
        option.set_status(not option.get_status())
        self.__update_indicator_label()
        self.__update_menu()
        self.config.persist()

    def __get_exchange_price_label(self, crypto_currency, price, large=True):
        if large:
            return crypto_currency + ' - ' + str(price) + self.real_currency_label
        else:
            return str(price) + self.real_currency_label

    def __get_icon_path(self):
        if self.config.is_theme_monochrome():
            return join(path.dirname(path.abspath(__file__)), '../img', '%s.svg' % ICON_MONOCHROME)
        else:
            return join(path.dirname(path.abspath(__file__)), '../img', '%s.svg' % ICON_COLOR)

    def __open_store(self, _):
        webbrowser.open(self.store_url)
