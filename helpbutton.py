# Main author:
# Copyright (C) 2012, Gonzalo Odiard <godiard@laptop.org>
# Minor changes and maintaining tasks:
# Copyright (C) 2012, Agustin Zubiaga <aguz@sugarlabs.org>
# Copyright (C) 2012, Daniel Francis <francis@sugarlabs.org>
# Copyright (C) 2012, Manuel Kaufmann <humitos@gmail.com>
# Copyright (C) 2025 MostlyK
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
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

# HelpButton widget

from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from sugar4.graphics.toolbutton import ToolButton
from sugar4.graphics.icon import Icon
from sugar4.graphics import style


class HelpButton(Gtk.Box):

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        help_button = ToolButton('toolbar-help')
        help_button.set_tooltip(_('Help'))
        self.append(help_button)

        self._palette = help_button.get_palette()

        # GTK4: Need to get screen size differently
        display = Gdk.Display.get_default()
        monitor = display.get_monitors().get_item(0)
        geometry = monitor.get_geometry()

        sw = Gtk.ScrolledWindow()
        sw.set_size_request(int(geometry.width / 2.8),
                            geometry.height - style.GRID_CELL_SIZE * 3)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._vbox.set_homogeneous(False)

        # GTK4: ScrolledWindow doesn't need viewport for Box
        sw.set_child(self._vbox)

        self._palette.set_content(sw)
        # GTK4: show_all() removed, just show() is enough
        sw.show()

        help_button.connect('clicked', self.__help_button_clicked_cb)

    def __help_button_clicked_cb(self, button):
        self._palette.popup(immediate=True)

    def add_section(self, section_text, icon=None):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label()
        label.set_justify(Gtk.Justification.FILL)
        label.set_use_markup(True)
        label.set_markup('<b>%s</b>' % section_text)
        # GTK4: set_line_wrap removed, labels wrap automatically
        label.set_halign(Gtk.Align.START)
        hbox.append(label)
        label.show()
        if icon is not None:
            _icon = Icon(icon_name=icon)
            hbox.append(_icon)
        # GTK4: show_all() removed, just show() is enough
        hbox.show()
        self._vbox.append(hbox)

    def add_paragraph(self, text, icon=None):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label(label=text)
        label.set_justify(Gtk.Justification.FILL)
        # GTK4: set_line_wrap removed, labels wrap automatically
        label.set_halign(Gtk.Align.START)
        hbox.append(label)
        label.show()

        if icon is not None:
            _icon = Icon(icon_name=icon)
            hbox.append(_icon)

        # GTK4: show_all() removed, just show() is enough
        hbox.show()
        self._vbox.append(hbox)
