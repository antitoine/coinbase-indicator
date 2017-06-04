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

MENU_ITEM_PRICE = 'price_'
MENU_ITEM_REFRESH = 'refresh'
MENU_ITEM_SETTINGS = 'settings_'
MENU_ITEM_QUIT = 'quit'

ICON_MONOCHROME = 'icon-0'
ICON_COLOR = 'icon-1'


class Ui(object):

    def __init__(self, app_id, crypto_currencies, real_currency, store_url, refresh_fc, quit_fc, config):
        self.real_currency_label = ''
        self.store_url = store_url
        self.config = config
        self.refresh_fc = refresh_fc
        self.quit_fc = quit_fc

        self.indicator = appindicator.Indicator.new(app_id, self.__get_icon_path(), appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_label('', '')
        notify.init(app_id)
        self.change_real_currency(real_currency)

        self.__init_menu(crypto_currencies)

    def update_icon(self):
        self.indicator.set_icon(self.__get_icon_path())

    def update_prices(self, crypto_currencies):
        label = ''
        for crypto_currency in crypto_currencies:
            self.menu_items[MENU_ITEM_PRICE + crypto_currency].get_child().set_text(
                self.__get_exchange_price_label(crypto_currency, crypto_currencies[crypto_currency])
            )
            self.menu_items[MENU_ITEM_PRICE + crypto_currency].show()
            if self.config.has_crypto_currency_option(crypto_currency) and self.config.get_crypto_currency_option(crypto_currency).get_status():
                label += '  ' + self.__get_exchange_price_label(crypto_currency, crypto_currencies[crypto_currency], False)
        self.indicator.set_label(label, '')

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
        if self.config.get_notification_option().get_status():
            notify.Notification.new('<b>Coinbase Indicator</b>', msg, self.__get_icon_path(),).show()

    def display(self):
        gtk.main()

    def close(self):
        notify.uninit()
        gtk.main_quit()

    def __init_menu(self, crypto_currencies):
        self.menu = gtk.Menu()

        self.menu_items = {}
        for crypto_currency in crypto_currencies:
            item = gtk.MenuItem(self.__get_exchange_price_label(crypto_currency, crypto_currencies[crypto_currency]))
            item.connect('activate', self.__open_store)
            self.menu_items[MENU_ITEM_PRICE + crypto_currency] = item
            self.menu.append(item)

        self.menu.append(gtk.SeparatorMenuItem('Refresh'))

        item_refresh = gtk.MenuItem('Refresh prices')
        item_refresh.connect('activate', lambda _: self.refresh_fc())
        self.menu_items[MENU_ITEM_REFRESH] = item_refresh
        self.menu.append(item_refresh)

        self.menu.append(gtk.SeparatorMenuItem("Settings"))

        options = self.config.get_options()
        for option_key in options:
            item = gtk.CheckMenuItem(options[option_key].get_label(), active=options[option_key].get_status())
            item.connect("activate", lambda _, key: self.__toggle_option_status(key), option_key)
            self.menu_items[MENU_ITEM_SETTINGS + option_key] = item
            self.menu.append(item)

        self.menu.append(gtk.SeparatorMenuItem('Quit'))

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', lambda _: self.quit_fc())
        self.menu_items[MENU_ITEM_QUIT] = item_quit
        self.menu.append(item_quit)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

    def __toggle_option_status(self, key):
        option = self.config.get_options()[key]
        option.set_status(not option.get_status())
        self.config.persist()
        self.refresh_fc()

    def __get_exchange_price_label(self, crypto_currency, price, large=True):
        if large:
            return '1 ' + crypto_currency + ' = ' + str(price) + self.real_currency_label
        else:
            return str(price) + self.real_currency_label

    def __get_icon_path(self):
        if self.config.get_theme_monochrome_option().get_status():
            return join(getcwd(), 'img', '%s.svg' % ICON_MONOCHROME)
        else:
            return join(getcwd(), 'img', '%s.svg' % ICON_COLOR)

    def __open_store(self, _):
        webbrowser.open(self.store_url)
