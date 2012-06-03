#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2006, Red Hat, Inc.
# Copyright (C) 2011, One Laptop Per Child
# Copyright (C) 2009, Tomeu Vizoso, Simon Schampijer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#,
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

from sugar3.graphics.icon import Icon


class TabAdd(Gtk.Button):
    __gtype_name__ = 'BrowseTabAdd'

    __gsignals__ = {
        'tab-added': (GObject.SignalFlags.RUN_FIRST,
                      None,
                      ([])),
    }

    def __init__(self):
        GObject.GObject.__init__(self)

        add_tab_icon = Icon(icon_name='add')
        self.props.relief = Gtk.ReliefStyle.NONE
        self.props.focus_on_click = False
        icon_box = Gtk.HBox()
        icon_box.pack_start(add_tab_icon, True, False, 0)
        self.add(icon_box)
        self.connect('clicked', self.__button_clicked_cb)
        self.set_name('browse-tab-add')
        add_tab_icon.show()
        icon_box.show()
        self.show()

    def __button_clicked_cb(self, button):
        self.emit('tab-added')


class BrowserNotebook(Gtk.Notebook):
    __gtype_name__ = 'BrowseNotebook'

    __gsignals__ = {
        'tab-added': (GObject.SignalFlags.RUN_FIRST,
                      None,
                      ([])),
    }

    """Handle an extra tab at the end with an Add Tab button."""

    def __init__(self):
        GObject.GObject.__init__(self)

        self.first_expose = True
        self.connect("draw", self._draw_cb)
        self._tab_add = TabAdd()
        self._tab_add.connect('tab-added', self.on_add_tab)
        self.set_action_widget(self._tab_add, Gtk.PackType.END)
        self._tab_add.show()

    def _draw_cb(self, widget, event):
        if self.first_expose:
            self.update_tab_sizes()
            self.first_expose = False

    def on_add_tab(self, obj):
        self.emit('tab-added')

    def update_tab_sizes(self):
        n_pages = self.get_n_pages()
        canvas_size = self.get_allocation()

        # FIXME
        # overlap_size = self.style_get_property('tab-overlap') * n_pages - 1
        overlap_size = 0
        allowed_size = canvas_size.width - overlap_size

        tab_new_size = int(float(allowed_size) / (n_pages) -\
                           self._tab_add.get_allocation().width - 5)

        for page_idx in range(n_pages):
            page = self.get_nth_page(page_idx)
            label = self.get_tab_label(page)
            label.update_size(tab_new_size)


class TabLabel(Gtk.HBox):
    __gtype_name__ = 'BrowseTabLabel'

    __gsignals__ = {
        'tab-close': (GObject.SignalFlags.RUN_FIRST,
                      None,
                      ([GObject.TYPE_PYOBJECT])),
    }

    def __init__(self, child):
        GObject.GObject.__init__(self)

        self.child = child
        self._label = Gtk.Label(label="")
        self._label.set_ellipsize(Pango.EllipsizeMode.END)
        self._label.set_alignment(0, 0.5)
        self.pack_start(self._label, True, True, 0)
        self._label.show()

        close_tab_icon = Icon(icon_name='close-tab')
        button = Gtk.Button()
        button.props.relief = Gtk.ReliefStyle.NONE
        button.props.focus_on_click = False
        icon_box = Gtk.HBox()
        icon_box.pack_start(close_tab_icon, True, False, 0)
        button.add(icon_box)
        button.connect('clicked', self.__button_clicked_cb)
        button.set_name('browse-tab-close')
        self.pack_start(button, False, True, 0)
        close_tab_icon.show()
        icon_box.show()
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
