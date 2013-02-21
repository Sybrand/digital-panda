import logging
import gtk
import appindicator
import sys
import os

def run():
    logging.error('Wups - we''re trying to get Ubuntu 12.10 to work!')
    icon_theme_path = os.path.join(sys.path[0], 'gfx')
    #'/home/sybrand/repos/digital-panda/panda-tray/gfx'
    logging.info('set icon theme path = %s' % icon_theme_path)
    ind = appindicator.Indicator ("Digital Panda",
        "digitalpandahead_icon",
        appindicator.CATEGORY_APPLICATION_STATUS,
        icon_theme_path=icon_theme_path)
    ind.set_status (appindicator.STATUS_ACTIVE)
    ind.set_attention_icon ("digitalpandahead")

    # create a menu
    menu = gtk.Menu()

    menu_item = gtk.MenuItem('Open Digital Panda folder')
    menu.append(menu_item)
    menu_item.show()

    menu_item = gtk.MenuItem('Settings...')
    menu.append(menu_item)
    menu_item.show()

    menu_item = gtk.MenuItem('Quit')
    menu.append(menu_item)
    menu_item.connect('activate', gtk.main_quit, 'Quit')
    menu_item.show()

    ind.set_menu(menu)

    gtk.main()
