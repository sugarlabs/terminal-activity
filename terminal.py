# Copyright (C) 2007, Eduardo Silva <edsiper@gmail.com>.
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

import os
import logging
from gettext import gettext as _

import gtk
import dbus

from sugar.activity import activity
from sugar import env

import ConfigParser
import os.path

import vte
import pango

class TerminalActivity(activity.Activity):

    def __init__(self, handle):

        activity.Activity.__init__(self, handle)
        logging.debug('Starting the Terminal activity')
        self.set_title(_('Terminal Activity'))

        # CANVAS
        terminal = Terminal()
        self.set_canvas(terminal)

        # TOOLBAR
        toolbox = activity.ActivityToolbox(self)
        toolbox.show()

        self.set_toolbox(toolbox)
        self.show_all()
        
        # Dirty hide()
        toolbar = toolbox.get_activity_toolbar()
        toolbar.share.hide()
        toolbar.keep.hide()

class Terminal(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self, False, 4)

        self._vte = vte.Terminal()
        self._configure_vte()
        self._vte.set_size(100, 5)
        self._vte.set_size_request(200, 450)
        self._vte.show()
        self.pack_start(self._vte)

        self._scrollbar = gtk.VScrollbar(self._vte.get_adjustment())
        self._scrollbar.show()
        self.pack_start(self._scrollbar, False, False, 0)

        self._vte.connect("child-exited", lambda term: term.fork_command())

        self._vte.fork_command()

    def _configure_vte(self):
        conf = ConfigParser.ConfigParser()

        conf_file = os.path.join(env.get_profile_path(), 'terminalrc')
        
        if os.path.isfile(conf_file):
            f = open(conf_file, 'r')
            conf.readfp(f)
            f.close()
        else:
            conf.add_section('terminal')

        if conf.has_option('terminal', 'font'):
            font = conf.get('terminal', 'font')
        else:
            font = 'Monospace 8'
            conf.set('terminal', 'font', font)
        self._vte.set_font(pango.FontDescription(font))

        if conf.has_option('terminal', 'fg_color'):
            fg_color = conf.get('terminal', 'fg_color')
        else:
            fg_color = '#000000'
            conf.set('terminal', 'fg_color', fg_color)
        if conf.has_option('terminal', 'bg_color'):
            bg_color = conf.get('terminal', 'bg_color')
        else:
            bg_color = '#FFFFFF'
            conf.set('terminal', 'bg_color', bg_color)
        self._vte.set_colors(gtk.gdk.color_parse (fg_color),
                            gtk.gdk.color_parse (bg_color),
                            [])
                            
        if conf.has_option('terminal', 'cursor_blink'):
            blink = conf.getboolean('terminal', 'cursor_blink')
        else:
            blink = False
            conf.set('terminal', 'cursor_blink', blink)
        
        self._vte.set_cursor_blinks(blink)

        if conf.has_option('terminal', 'bell'):
            bell = conf.getboolean('terminal', 'bell')
        else:
            bell = False
            conf.set('terminal', 'bell', bell)
        self._vte.set_audible_bell(bell)
        
        if conf.has_option('terminal', 'scrollback_lines'):
            scrollback_lines = conf.getint('terminal', 'scrollback_lines')
        else:
            scrollback_lines = 1000
            conf.set('terminal', 'scrollback_lines', scrollback_lines)
            
        self._vte.set_scrollback_lines(scrollback_lines)
        
        self._vte.set_allow_bold(True)
        
        if conf.has_option('terminal', 'scroll_on_keystroke'):
            scroll_key = conf.getboolean('terminal', 'scroll_on_keystroke')
        else:
            scroll_key = False
            conf.set('terminal', 'scroll_on_keystroke', scroll_key)
        self._vte.set_scroll_on_keystroke(scroll_key)
        
        if conf.has_option('terminal', 'scroll_on_output'):
            scroll_output = conf.getboolean('terminal', 'scroll_on_output')
        else:
            scroll_output = False
            conf.set('terminal', 'scroll_on_output', scroll_output)
        self._vte.set_scroll_on_output(scroll_output)
        
        if conf.has_option('terminal', 'emulation'):
            emulation = conf.get('terminal', 'emulation')
        else:
            emulation = 'xterm'
            conf.set('terminal', 'emulation', emulation)
        self._vte.set_emulation(emulation)
        
        if conf.has_option('terminal', 'visible_bell'):
            visible_bell = conf.getboolean('terminal', 'visible_bell')
        else:
            visible_bell = False
            conf.set('terminal', 'visible_bell', visible_bell)
        self._vte.set_visible_bell(visible_bell)
        
        conf.write(open(conf_file, 'w'))
        
    def on_gconf_notification(self, client, cnxn_id, entry, what):
        self.reconfigure_vte()

    def on_vte_button_press(self, term, event):
        if event.button == 3:
            self.do_popup(event)
            return True

    def on_vte_popup_menu(self, term):
        pass
