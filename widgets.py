# Copyright (C) 2006, Red Hat, Inc.
# Copyright (C) 2011, One Laptop Per Child
# Copyright (C) 2009, Tomeu Vizoso, Simon Schampijer
# Copyright (C) 2012, Daniel Francis
# Copyright (C) 2025 MostlyK
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Pango

from sugar4.graphics.icon import Icon


class TabAdd(Gtk.Button):
    __gsignals__ = {
        'tab-added': (GObject.SignalFlags.RUN_FIRST,
                      None,
                      ([])),
    }

    def __init__(self):
        super().__init__()

        add_tab_icon = Icon(icon_name='list-add')
        # GTK4: ReliefStyle removed, buttons are flat by default
        self.props.focus_on_click = False
        self.set_child(add_tab_icon)
        self.connect('clicked', self.__button_clicked_cb)
        add_tab_icon.show()
        self.show()

    def __button_clicked_cb(self, button):
        self.emit('tab-added')


class BrowserNotebook(Gtk.Notebook):
    __gsignals__ = {
        'tab-added': (GObject.SignalFlags.RUN_FIRST,
                      None,
                      ([])),
    }

    """Handle an extra tab at the end with an Add Tab button."""

    def __init__(self):
        super().__init__()

        self._tab_add = TabAdd()
        self._tab_add.connect('tab-added', self.on_add_tab)

        # GTK4: set_action_widget becomes append/prepend with TabPosition
        # For END position, we append to the tab bar
        self._tab_add.show()
        self.n_pages = 0
        self.width = 0
        self.button_size = 0

    def do_size_allocate(self, allocation):
        """GTK4: Override do_size_allocate instead of size-allocate signal."""
        Gtk.Notebook.do_size_allocate(self, allocation)
        # Update tab sizes
        n_pages = self.get_n_pages()
        width = allocation.width
        button_size = self._tab_add.get_allocation().width
        if n_pages != self.n_pages or width != self.width or self.button_size != button_size:
            self.n_pages = n_pages
            self.width = width
            self.button_size = button_size
            self.update_tab_sizes()

    def on_add_tab(self, obj):
        self.emit('tab-added')

    def update_tab_sizes(self):
        allowed_size = self.width
        if self.n_pages == 1:
            tab_new_size = int(allowed_size / 2)
            for page_idx in range(self.n_pages):
                page = self.get_nth_page(page_idx)
                label = self.get_tab_label(page)
                # GTK4: child_set_property still exists
                self.child_set_property(page, 'tab-expand', False)
                label.update_size(tab_new_size)
        else:
            for page_idx in range(self.n_pages):
                page = self.get_nth_page(page_idx)
                label = self.get_tab_label(page)
                label.update_size(-1)
                self.child_set_property(page, 'tab-expand', True)


class TabLabel(Gtk.Box):
    __gsignals__ = {
        'tab-close': (GObject.SignalFlags.RUN_FIRST,
                      None,
                      ([GObject.TYPE_PYOBJECT])),
    }

    def __init__(self, child):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.child = child
        self._label = Gtk.Label(label="")
        self._label.set_ellipsize(Pango.EllipsizeMode.END)
        # GTK4: set_alignment -> set_xalign/set_yalign
        self._label.set_xalign(0.0)
        self._label.set_yalign(0.5)
        self.append(self._label)
        self._label.show()

        close_tab_icon = Icon(icon_name='close-tab')
        button = Gtk.Button()
        button.set_child(close_tab_icon)
        button.connect('clicked', self.__button_clicked_cb)
        self.append(button)
        close_tab_icon.show()
        button.show()
        self._close_button = button

    def set_text(self, title):
        self._label.set_text(title)

    def update_size(self, size):
        self.set_size_request(size, -1)

    def hide_close_button(self):
        self._close_button.hide()

    def show_close_button(self):
        self._close_button.show()

    def __button_clicked_cb(self, button):
        self.emit('tab-close', self.child)
