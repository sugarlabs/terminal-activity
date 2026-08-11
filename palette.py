

from gi.repository import Gdk
from gi.repository import GLib, Gtk
from sugar4 import profile
from sugar4.graphics.palette import Palette
from sugar4.graphics.palettemenu import PaletteMenuItem
from gettext import gettext as _

from sugar4.graphics.palettewindow import Invoker


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
        lp = Gtk.GestureLongPress.new()
        lp.connect('pressed', self.__long_pressed_cb)
        browser.add_controller(lp)

    def __long_pressed_cb(self, controller, x, y):
        self.notify_right_click(x, y)
        return True

    def get_default_position(self):
        return self.AT_CURSOR

    def get_rect(self):
        if not self.parent:
            return Gdk.Rectangle()

        rect = Gdk.Rectangle()
        rect.x = 0
        rect.y = 0
        rect.width = self.parent.get_width()
        rect.height = self.parent.get_height()
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
        menu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(menu_box)
        menu_box.set_visible(True)

        if self._link:

            menu_item = PaletteMenuItem(_('Follow link'), 'browse-follow-link')
            menu_item.connect('clicked', self.__follow_activate_cb)
            menu_box.append(menu_item)
            menu_item.set_visible(True)

            menu_item = PaletteMenuItem(_('Copy link'), 'edit-copy')
            menu_item.icon.props.xo_color = profile.get_color()
            menu_item.connect('clicked', self.__copy_cb)
            menu_box.append(menu_item)
            menu_item.set_visible(True)

        if not self._link:
            menu_item = PaletteMenuItem(_('Copy text'), 'edit-copy')
            menu_item.icon.props.xo_color = profile.get_color()
            menu_item.connect('clicked', self.__copy_cb)
            menu_box.append(menu_item)
            menu_item.set_visible(True)

        menu_item = PaletteMenuItem(_('Paste text'), 'edit-paste')
        menu_item.icon.props.xo_color = profile.get_color()
        menu_item.connect('clicked', self.__paste_cb)
        menu_box.append(menu_item)
        menu_item.set_visible(True)

    def __follow_activate_cb(self, button):
        self.parent.browse_link_under_cursor()

    def __copy_cb(self, button):
        self.parent.copy_clipboard(None, self._link)

    def __paste_cb(self, button):
        self.parent.paste_clipboard()
