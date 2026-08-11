# Main author:
# Copyright (C) 2012, Gonzalo Odiard <godiard@laptop.org>
# Minor changes and maintaining tasks:
# Copyright (C) 2012, Agustin Zubiaga <aguz@sugarlabs.org>
# Copyright (C) 2012, Daniel Francis <francis@sugarlabs.org>
# Copyright (C) 2012, Manuel Kaufmann <humitos@gmail.com>
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

from sugar4.graphics.toolbutton import ToolButton
from sugar4.graphics.icon import Icon
from sugar4.graphics import style


def get_screen_size():
    display = Gdk.Display.get_default()
    if display:
        monitors = display.get_monitors()
        if monitors and monitors.get_n_items() > 0:
            monitor = monitors.get_item(0)
            return monitor.get_geometry()

    class FakeGeo:
        width = 1200
        height = 900
    return FakeGeo()


class HelpButton(ToolButton):

    def __init__(self, **kwargs):
        ToolButton.__init__(self, icon_name='toolbar-help', **kwargs)

        self.set_tooltip(_('Help'))

        self._palette = self.get_palette()

        geo = get_screen_size()
        sw = Gtk.ScrolledWindow()
        sw.set_size_request(int(geo.width / 2.8),
                            geo.height - style.GRID_CELL_SIZE * 3)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._vbox = Gtk.Box()
        self._vbox.set_orientation(Gtk.Orientation.VERTICAL)
        self._vbox.set_homogeneous(False)

        sw.set_child(self._vbox)

        self._palette.set_content(sw)

        self.connect('clicked', self.__help_button_clicked_cb)

    def __help_button_clicked_cb(self, button):
        self._palette.popup(immediate=True)

    def add_section(self, section_text, icon=None):
        hbox = Gtk.Box()
        label = Gtk.Label()
        label.set_justify(Gtk.Justification.FILL)
        label.set_use_markup(True)
        label.set_markup('<b>%s</b>' % section_text)
        label.set_wrap(True)
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        label.set_vexpand(True)
        label.set_margin_start(4)
        label.set_margin_end(4)
        hbox.append(label)
        if icon is not None:
            _icon = Icon(icon_name=icon)
            _icon.set_margin_start(10)
            _icon.set_margin_end(10)
            hbox.append(_icon)

        hbox.set_hexpand(True)
        hbox.set_vexpand(True)
        hbox.set_margin_top(5)
        hbox.set_margin_bottom(5)
        self._vbox.append(hbox)

    def add_paragraph(self, text, icon=None):
        hbox = Gtk.Box()
        label = Gtk.Label(label=text)
        label.set_justify(Gtk.Justification.FILL)
        label.set_wrap(True)
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        label.set_vexpand(True)
        label.set_margin_start(20)
        label.set_margin_end(20)
        hbox.append(label)

        if icon is not None:
            _icon = Icon(icon_name=icon)
            _icon.set_margin_start(20)
            _icon.set_margin_end(20)
            hbox.append(_icon)

        hbox.set_hexpand(True)
        hbox.set_vexpand(True)
        hbox.set_margin_top(3)
        hbox.set_margin_bottom(3)
        self._vbox.append(hbox)
