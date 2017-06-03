# Need package python-gi

import signal
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


APPINDICATOR_ID = 'coinbase_indicator'

ICON_INACTIVE = 'icon-0'
ICON_ACTIVE = 'icon-1'


def image_path(name):
    return join(getcwd(), 'img', '%s.svg' % name)


class CoinbaseAppIndicator(object):

    def __init__(self):
        notify.init(APPINDICATOR_ID)
        self.indicator = appindicator.Indicator.new(
            APPINDICATOR_ID, image_path(ICON_INACTIVE), appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.alarm = False

        self.update()

    def run(self):
        gtk.main()

    def update(self):
        self.__update_icon()
        self.__update_menu()

    def __update_icon(self):
        if self.alarm:
            self.indicator.set_icon(image_path(ICON_ACTIVE))
        else:
            self.indicator.set_icon(image_path(ICON_INACTIVE))

    def __update_menu(self):
        menu = gtk.Menu()

        item_btc = gtk.MenuItem('BTC')
        item_btc.connect('activate', self.on_open_coinbase)
        menu.append(item_btc)

        item_eth = gtk.MenuItem('ETH')
        item_eth.connect('activate', self.on_open_coinbase)
        menu.append(item_eth)

        item_ltc = gtk.MenuItem('LTC')
        item_ltc.connect('activate', self.on_open_coinbase)
        menu.append(item_ltc)

        menu.append(gtk.SeparatorMenuItem("Options"))

        item_refresh = gtk.MenuItem('Refresh')
        item_refresh.connect('activate', self.on_refresh)
        menu.append(item_refresh)

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.on_quit)
        menu.append(item_quit)

        menu.show_all()
        self.indicator.set_menu(menu)

    def quit(self):
        notify.uninit()
        gtk.main_quit()

    def open_coinbase(self):
        webbrowser.open('https://www.coinbase.com/')

    def on_quit(self, _): self.quit()

    def on_refresh(self, _): self.update()

    def on_open_coinbase(self, _): self.open_coinbase()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    CoinbaseAppIndicator().run()
