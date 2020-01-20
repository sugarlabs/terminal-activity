import logging
import tempfile

from gi.repository import Gdk
from gi.repository import GLib, Gtk, SugarGestures
from sugar3 import profile
from sugar3.graphics.palette import Palette
from sugar3.graphics.palettemenu import PaletteMenuItem, PaletteMenuItemSeparator
from gettext import gettext as _

from sugar3.graphics.palettewindow import Invoker


class ContentInvoker(Invoker):
    def __init__(self, parent, link):
        Invoker.__init__(self)
        self._position_hint = self.AT_CURSOR
        self.parent = parent
        self._link = link

        self.parent.connect('realize', self.__term_realize_cb)
        self.palette = TerminalPalette(self.parent, self._link)
        self.notify_right_click()

    def __term_realize_cb(self, browser):
        x11_window = browser.get_window()
        x11_window.set_events(x11_window.get_events() |
                              Gdk.EventMask.POINTER_MOTION_MASK |
                              Gdk.EventMask.TOUCH_MASK)

        lp = SugarGestures.LongPressController()
        lp.connect('pressed', self.__long_pressed_cb)
        lp.attach(browser, SugarGestures.EventControllerFlags.NONE)

    def __long_pressed_cb(self, controller, x, y):
        # We can't force a context menu, but we can fake a right mouse click
        event = Gdk.Event()
        event.type = Gdk.EventType.BUTTON_PRESS

        b = event.button
        b.type = Gdk.EventType.BUTTON_PRESS
        b.window = self.activity.get_window()
        b.time = Gtk.get_current_event_time()
        b.button = 3  # Right
        b.x = x
        b.y = y
        b.x_root, b.y_root = self.activity.get_window().get_root_coords(x, y)

        Gtk.main_do_event(event)
        return True

    def get_default_position(self):
        return self.AT_CURSOR

    def get_rect(self):
        allocation = self.activity.get_allocation()
        window = self.activity.get_window()
        if window is not None:
            res, x, y = window.get_origin()
        else:
            logging.warning(
                "Trying to position palette with invoker that's not realized.")
            x = 0
            y = 0

        x += allocation.x
        y += allocation.y

        width = allocation.width
        height = allocation.height

        rect = Gdk.Rectangle()
        rect.x = x
        rect.y = y
        rect.width = width
        rect.height = height
        return rect

    def get_toplevel(self):
        return None


class TerminalPalette(Palette):
    def __init__(self, parent, link=False):
        Palette.__init__(self)
        self.parent = parent
        self._link = link
        self.create()
        self.popup()

    def create(self):

        if self._link is not None:
            self.props.primary_text = GLib.markup_escape_text(self._link)
        else:
            self.props.primary_text = GLib.markup_escape_text(_('Terminal'))
        menu_box = Gtk.VBox()
        self.set_content(menu_box)
        menu_box.show()
        self._content.set_border_width(1)

        if self._link:

            menu_item = PaletteMenuItem(_('Follow link'), 'browse-follow-link')
            menu_item.connect('activate', self.__follow_activate_cb)
            menu_box.pack_start(menu_item, False, False, 0)
            menu_item.show()

            menu_item = PaletteMenuItem(_('Copy link'), 'edit-copy')
            menu_item.icon.props.xo_color = profile.get_color()
            menu_item.connect('activate', self.__copy_cb)
            menu_box.pack_start(menu_item, False, False, 0)
            menu_item.show()

        if not self._link:
            menu_item = PaletteMenuItem(_('Copy text'), 'edit-copy')
            menu_item.icon.props.xo_color = profile.get_color()
            menu_item.connect('activate', self.__copy_cb)
            menu_box.pack_start(menu_item, False, False, 0)
            menu_item.show()

        menu_item = PaletteMenuItem(_('Paste text'), 'edit-paste')
        menu_item.icon.props.xo_color = profile.get_color()
        menu_item.connect('activate', self.__paste_cb)
        menu_box.pack_start(menu_item, False, False, 0)
        menu_item.show()

    def __follow_activate_cb(self, button):
        self.parent.browse_link_under_cursor()

    def __copy_cb(self, button):
        self.parent.copy_clipboard(None, self._link)

    def __paste_cb(self, button):
        self.parent.paste_clipboard()