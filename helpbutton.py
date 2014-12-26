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
from gi.repository import GObject

from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.icon import Icon
from sugar3.graphics import style


class HelpButton(Gtk.ToolItem):

    def __init__(self, **kwargs):
        GObject.GObject.__init__(self)

        help_button = ToolButton('toolbar-help')
        help_button.set_tooltip(_('Help'))
        self.add(help_button)

        self._palette = help_button.get_palette()

        sw = Gtk.ScrolledWindow()
        sw.set_size_request(int(Gdk.Screen.width() / 2.8),
                            Gdk.Screen.height() - style.GRID_CELL_SIZE * 3)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._max_text_width = int(Gdk.Screen.width() / 3) - 600
        self._vbox = Gtk.Box()
        self._vbox.set_orientation(Gtk.Orientation.VERTICAL)
        self._vbox.set_homogeneous(False)
        self._vbox.set_border_width(10)

        hbox = Gtk.Box()
        hbox.pack_start(self._vbox, False, True, 0)

        sw.add_with_viewport(hbox)

        self._palette.set_content(sw)
        sw.show_all()

        help_button.connect('clicked', self.__help_button_clicked_cb)

    def __help_button_clicked_cb(self, button):
        self._palette.popup(immediate=True, state=1)

    def add_section(self, section_text):
        hbox = Gtk.Box()
        label = Gtk.Label()
        label.set_use_markup(True)
        label.set_markup('<b>%s</b>' % section_text)
        label.set_line_wrap(True)
        hbox.pack_start(label, False, False, 0)
        hbox.show_all()
        self._vbox.pack_start(hbox, False, False, padding=5)

    def add_paragraph(self, text, icon=None):
        hbox = Gtk.Box()
        label = Gtk.Label(label=text)
        label.set_justify(Gtk.Justification.LEFT)
        label.set_line_wrap(True)
        hbox.pack_start(label, False, False, 0)
        if icon is not None:
            _icon = Icon(icon_name=icon)
            hbox.add(_icon)
        hbox.show_all()
        self._vbox.pack_start(hbox, False, False, padding=5)
