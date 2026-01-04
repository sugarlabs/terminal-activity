# Copyright (C) 2025 MostlyK
# GTK4 Port of Terminal Activity Palette
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import logging

from gi.repository import Gdk
from gi.repository import GLib, Gtk
from sugar4 import profile
from sugar4.graphics.palette import Palette
from sugar4.graphics.palettemenu import PaletteMenuItem
from gettext import gettext as _

from sugar4.graphics.palettewindow import Invoker


class ContentInvoker(Invoker):
    def __init__(self, parent, link):
        super().__init__()
        self._position_hint = self.AT_CURSOR
        self.parent = parent
        self._link = link

        self.parent.connect('realize', self.__term_realize_cb)
        self.palette = TerminalPalette(self.parent, self._link)
        self.notify_right_click()

    def __term_realize_cb(self, browser):
        # GTK4: Event handling for mouse/touch is different
        # We use event controllers instead of setting window events directly
        # For now, we'll rely on the button-press-event handler in sugarterm.py

        # Note: Long press handling would need GestureLongPress in GTK4
        # For now, we skip this as the right-click should work
        pass

    def get_default_position(self):
        return self.AT_CURSOR

    def get_rect(self):
        allocation = self.parent.get_allocation()
        # GTK4: Get toplevel and its surface
        toplevel = self.parent.get_root()
        if toplevel is not None:
            native = toplevel.get_surface()
            if native is not None:
                # Try to get position from the surface
                # This is more complex in GTK4 due to Wayland
                res, x, y = False, 0, 0
                # Fallback to allocation
                if not res:
                    x, y = 0, 0
            else:
                logging.warning(
                    "Trying to position palette with invoker that's not realized.")
                x = 0
                y = 0
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
        return self.parent.get_root()


class TerminalPalette(Palette):
    def __init__(self, parent, link=False):
        super().__init__()
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
        menu_box.show()
        self._content.set_border_width(1)

        if self._link:

            menu_item = PaletteMenuItem(_('Follow link'), 'browse-follow-link')
            menu_item.connect('activate', self.__follow_activate_cb)
            menu_box.append(menu_item)
            menu_item.show()

            menu_item = PaletteMenuItem(_('Copy link'), 'edit-copy')
            menu_item.icon.props.xo_color = profile.get_color()
            menu_item.connect('activate', self.__copy_cb)
            menu_box.append(menu_item)
            menu_item.show()

        if not self._link:
            menu_item = PaletteMenuItem(_('Copy text'), 'edit-copy')
            menu_item.icon.props.xo_color = profile.get_color()
            menu_item.connect('activate', self.__copy_cb)
            menu_box.append(menu_item)
            menu_item.show()

        menu_item = PaletteMenuItem(_('Paste text'), 'edit-paste')
        menu_item.icon.props.xo_color = profile.get_color()
        menu_item.connect('activate', self.__paste_cb)
        menu_box.append(menu_item)
        menu_item.show()

    def __follow_activate_cb(self, button):
        self.parent.browse_link_under_cursor()

    def __copy_cb(self, button):
        self.parent.copy_clipboard(None, self._link)

    def __paste_cb(self, button):
        self.parent.paste_clipboard()
