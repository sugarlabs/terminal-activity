# Copyright (C) 2006, Red Hat, Inc.
# Copyright (C) 2011, One Laptop Per Child
# Copyright (C) 2009, Tomeu Vizoso, Simon Schampijer
# Copyright (C) 2012, Daniel Francis
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
        GObject.GObject.__init__(self)

        add_tab_icon = Icon(icon_name='list-add')
        self.set_has_frame(False)
        self.set_focus_on_click(False)
        self.set_child(add_tab_icon)
        self.connect('clicked', self.__button_clicked_cb)
        add_tab_icon.set_visible(True)
        self.set_visible(True)

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
        GObject.GObject.__init__(self)

        self._tab_add = TabAdd()
        self._tab_add.connect('tab-added', self.on_add_tab)
        self.set_action_widget(self._tab_add, Gtk.PackType.END)
        self._tab_add.set_visible(True)
        self.n_pages = 0
        self.width = 0
        self.button_size = 0

        self.connect('page-added', self._pages_changed_cb)
        self.connect('page-removed', self._pages_changed_cb)

    def _pages_changed_cb(self, notebook, child, page_num):
        self._check_tab_sizes()

    def do_size_allocate(self, width, height, baseline):
        Gtk.Notebook.do_size_allocate(self, width, height, baseline)
        self._check_tab_sizes()

    def _check_tab_sizes(self):
        """Update tab sizes when page count, width, or button size changes."""
        n_pages = self.get_n_pages()
        width = self.get_width()
        button_size = self._tab_add.get_width()
        if n_pages != self.n_pages or width != self.width \
                or self.button_size != button_size:
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
                self.get_page(page).set_property('tab-expand', False)
                label.update_size(tab_new_size)
        else:
            for page_idx in range(self.n_pages):
                page = self.get_nth_page(page_idx)
                label = self.get_tab_label(page)
                label.update_size(-1)
                self.get_page(page).set_property('tab-expand', True)


class TabLabel(Gtk.Box):
    __gsignals__ = {
        'tab-close': (GObject.SignalFlags.RUN_FIRST,
                      None,
                      ([GObject.TYPE_PYOBJECT])),
    }

    def __init__(self, child):
        GObject.GObject.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.child = child
        self._label = Gtk.Label(label="")
        self._label.set_ellipsize(Pango.EllipsizeMode.END)
        self._label.set_halign(Gtk.Align.START)
        self._label.set_valign(Gtk.Align.CENTER)
        self._label.set_hexpand(True)
        self._label.set_vexpand(True)
        self.append(self._label)
        self._label.set_visible(True)

        close_tab_icon = Icon(icon_name='close-tab')
        button = Gtk.Button()
        button.set_has_frame(False)
        button.set_child(close_tab_icon)
        button.connect('clicked', self.__button_clicked_cb)
        self.append(button)
        close_tab_icon.set_visible(True)
        button.set_visible(True)
        self._close_button = button

    def set_text(self, title):
        self._label.set_text(title)

    def update_size(self, size):
        self.set_size_request(size, -1)

    def hide_close_button(self):
        self._close_button.set_visible(False)

    def show_close_button(self):
        self._close_button.set_visible(True)

    def __button_clicked_cb(self, button):
        self.emit('tab-close', self.child)
