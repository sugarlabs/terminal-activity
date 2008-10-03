# Copyright (C) 2007, Eduardo Silva <edsiper@gmail.com>.
# Copyright (C) 2008, One Laptop Per Child
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
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.palette import Palette
import ConfigParser
import os.path

import vte
import pango

class TerminalActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        
        logging.debug('Starting the Terminal activity')
        
        self.set_title(_('Terminal Activity'))
        self.connect('key-press-event', self.__key_press_cb)

        toolbox = activity.ActivityToolbox(self)

        self._edit_toolbar = activity.EditToolbar()
        toolbox.add_toolbar(_('Edit'), self._edit_toolbar)
        self._edit_toolbar.show()
        self._edit_toolbar.undo.props.visible = False
        self._edit_toolbar.redo.props.visible = False
        self._edit_toolbar.separator.props.visible = False
        self._edit_toolbar.copy.connect('clicked', self._copy_cb)
        self._edit_toolbar.paste.connect('clicked', self._paste_cb)

        activity_toolbar = toolbox.get_activity_toolbar()
        # free up keyboard accelerators per #4646
        activity_toolbar.stop.props.accelerator = None

        # unneeded buttons (also frees up keyboard accelerators per #4646)
        activity_toolbar.remove(activity_toolbar.share)
        activity_toolbar.share = None
        activity_toolbar.remove(activity_toolbar.keep)
        activity_toolbar.keep = None

        # Add a button that will be used to become root easily.
        activity_toolbar.become_root = ToolButton('activity-become-root')
        activity_toolbar.become_root.set_tooltip(_('Become root'))
        activity_toolbar.become_root.connect('clicked',
                                             self._become_root_cb)
        activity_toolbar.insert(activity_toolbar.become_root, 2)
        activity_toolbar.become_root.show()

        self.set_toolbox(toolbox)
        toolbox.show()
        
        box = gtk.HBox(False, 4)

        self._vte = VTE()
        self._vte.set_scroll_on_keystroke(True)
        self._vte.connect("child-exited", lambda term: self.close())
        self._vte.show()

        scrollbar = gtk.VScrollbar(self._vte.get_adjustment())
        scrollbar.show()

        box.pack_start(self._vte)
        box.pack_start(scrollbar, False, False, 0)
        
        self.set_canvas(box)
        box.show()
        
        self._vte.grab_focus()

    def _copy_cb(self, button):
        if self._vte.get_has_selection():
            self._vte.copy_clipboard()

    def _paste_cb(self, button):
        self._vte.paste_clipboard()

    def _become_root_cb(self, button):
        self._vte.fork_command("/bin/su", ('/bin/su', '-'))

    def __key_press_cb(self, window, event):
        if event.state & gtk.gdk.CONTROL_MASK and event.state & gtk.gdk.SHIFT_MASK:
        
            if gtk.gdk.keyval_name(event.keyval) == "C":
                if self._vte.get_has_selection():
                    self._vte.copy_clipboard()              
                return True
            elif gtk.gdk.keyval_name(event.keyval) == "V":
                self._vte.paste_clipboard()
                return True
                
        return False

class VTE(vte.Terminal):
    def __init__(self):
        vte.Terminal.__init__(self)
        self._configure_vte()
        self.drag_dest_set(gtk.DEST_DEFAULT_MOTION|
                gtk.DEST_DEFAULT_DROP,
               [('text/plain', 0, 0),
                ('STRING', 0, 1)],
               gtk.gdk.ACTION_DEFAULT|
               gtk.gdk.ACTION_COPY)
        self.connect('drag_data_received', self.data_cb)
        
        os.chdir(os.environ["HOME"])
        self.fork_command()
    
    def data_cb(self, widget, context, x, y, selection, target, time):
        self.feed_child(selection.data)
        context.finish(True, False, time)
        return True
    
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
        self.set_font(pango.FontDescription(font))

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
        self.set_colors(gtk.gdk.color_parse (fg_color),
                            gtk.gdk.color_parse (bg_color),
                            [])
                            
        if conf.has_option('terminal', 'cursor_blink'):
            blink = conf.getboolean('terminal', 'cursor_blink')
        else:
            blink = False
            conf.set('terminal', 'cursor_blink', blink)
        
        self.set_cursor_blinks(blink)

        if conf.has_option('terminal', 'bell'):
            bell = conf.getboolean('terminal', 'bell')
        else:
            bell = False
            conf.set('terminal', 'bell', bell)
        self.set_audible_bell(bell)
        
        if conf.has_option('terminal', 'scrollback_lines'):
            scrollback_lines = conf.getint('terminal', 'scrollback_lines')
        else:
            scrollback_lines = 1000
            conf.set('terminal', 'scrollback_lines', scrollback_lines)
            
        self.set_scrollback_lines(scrollback_lines)
        self.set_allow_bold(True)
        
        if conf.has_option('terminal', 'scroll_on_keystroke'):
            scroll_key = conf.getboolean('terminal', 'scroll_on_keystroke')
        else:
            scroll_key = False
            conf.set('terminal', 'scroll_on_keystroke', scroll_key)
        self.set_scroll_on_keystroke(scroll_key)

        if conf.has_option('terminal', 'scroll_on_output'):
            scroll_output = conf.getboolean('terminal', 'scroll_on_output')
        else:
            scroll_output = False
            conf.set('terminal', 'scroll_on_output', scroll_output)
        self.set_scroll_on_output(scroll_output)
        
        if conf.has_option('terminal', 'emulation'):
            emulation = conf.get('terminal', 'emulation')
        else:
            emulation = 'xterm'
            conf.set('terminal', 'emulation', emulation)
        self.set_emulation(emulation)

        if conf.has_option('terminal', 'visible_bell'):
            visible_bell = conf.getboolean('terminal', 'visible_bell')
        else:
            visible_bell = False
            conf.set('terminal', 'visible_bell', visible_bell)
        self.set_visible_bell(visible_bell)
        conf.write(open(conf_file, 'w'))

    def on_gconf_notification(self, client, cnxn_id, entry, what):
        self.reconfigure_vte()

    def on_vte_button_press(self, term, event):
        if event.button == 3:
            self.do_popup(event)
            return True

    def on_vte_popup_menu(self, term):
        pass
