# Copyright (C) 2007, Eduardo Silva <edsiper@gmail.com>.
# Copyright (C) 2008, One Laptop Per Child
# Copyright (C) 2009, Simon Schampijer
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
import sys
import simplejson
import ConfigParser

import logging
from gettext import gettext as _

import gtk
import vte
import pango

from sugar.graphics.toolbutton import ToolButton
from sugar.activity import activity
from sugar import env

# Attempt to import the new toolbar classes.  If the import fails,
# fall back to the old toolbar style.
try:
    from sugar.graphics.toolbarbox import ToolbarBox
    from sugar.graphics.toolbarbox import ToolbarButton
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton
    NEW_TOOLBARS = True
except ImportError:
    from sugar.activity.activity import ActivityToolbox
    NEW_TOOLBARS = False


MASKED_ENVIRONMENT = [
    'DBUS_SESSION_BUS_ADDRESS',
    'PPID']

log = logging.getLogger('Terminal')
log.setLevel(logging.DEBUG)
logging.basicConfig()


class TerminalActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.max_participants = 1

        edit_toolbar = self._create_edit_toolbar()
        edit_toolbar.show()

        view_toolbar = self._create_view_toolbar()
        view_toolbar.show()

        self._delete_tab_toolbar = None
        self._previous_tab_toolbar = None
        self._next_tab_toolbar = None
        tab_toolbar = self._create_tab_toolbar()
        tab_toolbar.show()

        # Add a button that will be used to become root easily.
        root_button = ToolButton('activity-become-root')
        root_button.set_tooltip(_('Become root'))
        root_button.connect('clicked', self.__become_root_cb)
        root_button.show()

        if NEW_TOOLBARS:
            toolbar_box = ToolbarBox()

            activity_button = ActivityToolbarButton(self)
            toolbar_box.toolbar.insert(activity_button, 0)
            activity_button.page.keep.props.accelerator = '<Ctrl><Shift>S'
            activity_button.show()
    
            edit_toolbar_button = ToolbarButton(
                    page=edit_toolbar,
                    icon_name='toolbar-edit')
            toolbar_box.toolbar.insert(edit_toolbar_button, -1)
            edit_toolbar_button.show()

            view_toolbar_button = ToolbarButton(
                    page=view_toolbar,
                    icon_name='toolbar-view')
            toolbar_box.toolbar.insert(view_toolbar_button, -1)
            view_toolbar_button.show()

            tab_toolbar_button = ToolbarButton(
                    page=tab_toolbar,
                    icon_name='toolbar-tab')
            toolbar_box.toolbar.insert(tab_toolbar_button, -1)
            tab_toolbar_button.show()

            toolbar_box.toolbar.insert(root_button, -1)

            separator = gtk.SeparatorToolItem()
            separator.props.draw = False
            separator.set_expand(True)
            toolbar_box.toolbar.insert(separator, -1)
            separator.show()
    
            stop_button = StopButton(self)
            stop_button.props.accelerator = '<Ctrl><Shift>Q'
            toolbar_box.toolbar.insert(stop_button, -1)
            stop_button.show()
    
            self.set_toolbar_box(toolbar_box)
            toolbar_box.show()
    
        else:
            toolbox = ActivityToolbox(self)
            toolbox.add_toolbar(_('Edit'), edit_toolbar)
            toolbox.add_toolbar(_('View'), view_toolbar)
            toolbox.add_toolbar(_('Tab'), tab_toolbar)

            self.set_toolbox(toolbox)
            toolbox.show()

        self._notebook = gtk.Notebook()
        self._notebook.set_property("tab-pos", gtk.POS_TOP)
        self._notebook.set_scrollable(True)
        self._notebook.show()

        self.set_canvas(self._notebook)

        self._create_tab(None)

    def _create_edit_toolbar(self):
        edit_toolbar = activity.EditToolbar()
        edit_toolbar.undo.props.visible = False
        edit_toolbar.redo.props.visible = False
        edit_toolbar.separator.props.visible = False
        edit_toolbar.copy.connect('clicked', self.__copy_cb)
        edit_toolbar.copy.props.accelerator = '<Ctrl><Shift>C'
        edit_toolbar.paste.connect('clicked', self.__paste_cb)
        edit_toolbar.paste.props.accelerator = '<Ctrl><Shift>V'
        return edit_toolbar

    def __copy_cb(self, button):
        vt = self._notebook.get_nth_page(self._notebook.get_current_page()).vt
        if vt.get_has_selection():
            vt.copy_clipboard()

    def __paste_cb(self, button):
        vt = self._notebook.get_nth_page(self._notebook.get_current_page()).vt
        vt.paste_clipboard()

    def _create_view_toolbar(self):
        view_toolbar = gtk.Toolbar()
        fullscreen_button = ToolButton('view-fullscreen')
        fullscreen_button.set_tooltip(_("Fullscreen"))
        fullscreen_button.props.accelerator = '<Alt>Return'
        fullscreen_button.connect('clicked', self.__fullscreen_cb)
        view_toolbar.insert(fullscreen_button, -1)
        fullscreen_button.show()
        return view_toolbar

    def __fullscreen_cb(self, button):
        self.fullscreen()

    def _create_tab_toolbar(self):
        tab_toolbar = gtk.Toolbar()
        new_tab_button = ToolButton('tab-add')
        new_tab_button.set_tooltip(_("Open New Tab"))
        new_tab_button.props.accelerator = '<Ctrl><Shift>T'
        new_tab_button.connect('clicked', self.__open_tab_cb)
        tab_toolbar.insert(new_tab_button, -1)
        new_tab_button.show()

        self._delete_tab_button = ToolButton('tab-remove')
        self._delete_tab_button.set_tooltip(_("Close Tab"))
        self._delete_tab_button.props.accelerator = '<Ctrl><Shift>X'
        self._delete_tab_button.props.sensitive = False
        self._delete_tab_button.connect('clicked', self.__close_tab_cb)
        tab_toolbar.insert(self._delete_tab_button, -1)
        self._delete_tab_button.show()

        self._previous_tab_button = ToolButton('tab-previous')
        self._previous_tab_button.set_tooltip(_("Previous Tab"))
        self._previous_tab_button.props.accelerator = '<Ctrl><Shift>Left'
        self._previous_tab_button.props.sensitive = False
        self._previous_tab_button.connect('clicked', self.__prev_tab_cb)
        tab_toolbar.insert(self._previous_tab_button, -1)
        self._previous_tab_button.show()

        self._next_tab_button = ToolButton('tab-next')
        self._next_tab_button.set_tooltip(_("Next Tab"))
        self._next_tab_button.props.accelerator = '<Ctrl><Shift>Right'
        self._next_tab_button.props.sensitive = False
        self._next_tab_button.connect('clicked', self.__next_tab_cb)
        tab_toolbar.insert(self._next_tab_button, -1)
        self._next_tab_button.show()
        return tab_toolbar

    def __open_tab_cb(self, btn):
        index = self._create_tab(None)
        self._notebook.page = index
        if self._notebook.get_n_pages() == 2:
            self._delete_tab_button.props.sensitive = True
            self._previous_tab_button.props.sensitive = True
            self._next_tab_button.props.sensitive = True

    def __close_tab_cb(self, btn):
        self._close_tab(self._notebook.props.page)
        if self._notebook.get_n_pages() == 1:
            self._delete_tab_button.props.sensitive = False
            self._previous_tab_button.props.sensitive = False
            self._next_tab_button.props.sensitive = False

    def __prev_tab_cb(self, btn):
        if self._notebook.props.page == 0:
            self._notebook.props.page = self._notebook.get_n_pages() - 1
        else:
            self._notebook.props.page = self._notebook.props.page - 1
        vt = self._notebook.get_nth_page(self._notebook.get_current_page()).vt
        vt.grab_focus()

    def __next_tab_cb(self, btn):
        if self._notebook.props.page == self._notebook.get_n_pages() - 1:
            self._notebook.props.page = 0
        else:
            self._notebook.props.page = self._notebook.props.page + 1
        vt = self._notebook.get_nth_page(self._notebook.get_current_page()).vt
        vt.grab_focus()

    def _close_tab(self, index):
        self._notebook.remove_page(index)
        if self._notebook.get_n_pages() == 0:
            self.close()

    def __tab_child_exited_cb(self, vt):
        for i in range(self._notebook.get_n_pages()):
            if self._notebook.get_nth_page(i).vt == vt:
                self._close_tab(i)
                return

    def __tab_title_changed_cb(self, vt):
        for i in range(self._notebook.get_n_pages()):
            if self._notebook.get_nth_page(i).vt == vt:
                label = self._notebook.get_nth_page(i).label
                label.set_text(vt.get_window_title())
                return

    def __drag_data_received_cb(self, widget, context, x, y, selection,
                                target, time):
        widget.feed_child(selection.data)
        context.finish(True, False, time)
        return True

    def _create_tab(self, tab_state):
        vt = vte.Terminal()
        vt.connect("child-exited", self.__tab_child_exited_cb)
        vt.connect("window-title-changed", self.__tab_title_changed_cb)

        # FIXME have to resend motion events to parent, see #1402
        vt.connect('motion-notify-event', self.__motion_notify_cb)

        vt.drag_dest_set(gtk.DEST_DEFAULT_MOTION|gtk.DEST_DEFAULT_DROP,
               [('text/plain', 0, 0), ('STRING', 0, 1)],
               gtk.gdk.ACTION_DEFAULT|
               gtk.gdk.ACTION_COPY)
        vt.connect('drag_data_received', self.__drag_data_received_cb)

        self._configure_vt(vt)

        vt.show()

        label = gtk.Label()

        scrollbar = gtk.VScrollbar(vt.get_adjustment())
        scrollbar.show()

        box = gtk.HBox()
        box.pack_start(vt)
        box.pack_start(scrollbar)

        box.vt = vt
        box.label = label

        index = self._notebook.append_page(box, label)
        self._notebook.show_all()

        # Uncomment this to only show the tab bar when there is at least
        # one tab. I think it's useful to always see it, since it displays
        # the 'window title'.
        # self._notebook.props.show_tabs = self._notebook.get_n_pages() > 1

        # Launch the default shell in the HOME directory.
        os.chdir(os.environ["HOME"])

        if tab_state:
            # Restore the environment.
            # This is currently not enabled.
            environment = tab_state['env']

            filtered_env = []
            for e in environment:
                var, sep, value = e.partition('=')
                if var not in MASKED_ENVIRONMENT:
                    filtered_env.append(var + sep + value)

            # TODO: Make the shell restore these environment variables,
            # then clear out TERMINAL_ENV.
            # os.environ['TERMINAL_ENV'] = '\n'.join(filtered_env)

            # Restore the working directory.
            if 'cwd' in tab_state and os.path.exists(tab_state['cwd']):
                try:                                           
                    os.chdir(tab_state['cwd'])
                except:
                    # ACLs may deny access
                    sys.stdout.write("Could not chdir to " + tab_state['cwd'])

            # Restore the scrollback buffer.
            for l in tab_state['scrollback']:
                vt.feed(l + '\r\n')

        box.pid = vt.fork_command()

        self._notebook.props.page = index
        vt.grab_focus()

        return index

    def __motion_notify_cb(self, widget, event):
        self.canvas.parent.emit('motion-notify-event', event)

    def __become_root_cb(self, button):
        vt = self._notebook.get_nth_page(self._notebook.get_current_page()).vt
        vt.feed('\r\n')
        vt.fork_command("/bin/su", ('/bin/su', '-'))

    def __key_press_cb(self, window, event):
        # Escape keypresses are routed directly to the vte and then dropped.
        # This hack prevents Sugar from hijacking them and canceling
        # fullscreen mode.
        if gtk.gdk.keyval_name(event.keyval) == 'Escape':
            current_page = self._notebook.get_current_page()
            vt = self._notebook.get_nth_page(current_page).vt
            vt.event(event)
            return True

        return False

    def read_file(self, file_path):
        if self.metadata['mime_type'] != 'text/plain':
            return

        fd = open(file_path, 'r')
        text = fd.read()
        data = simplejson.loads(text)
        fd.close()

        data_file = file_path

        # Clean out any existing tabs.
        while self._notebook.get_n_pages():
            self._notebook.remove_page(0)

        # Create new tabs from saved state.
        for tab_state in data['tabs']:
            self._create_tab(tab_state)

        # Restore active tab.
        self._notebook.props.page = data['current-tab']

        # Create a blank one if this state had no terminals.
        if self._notebook.get_n_pages() == 0:
            self._create_tab(None)

        if self._notebook.get_n_pages() > 1:
            self._delete_tab_button.props.sensitive = True
            self._previous_tab_button.props.sensitive = True
            self._next_tab_button.props.sensitive = True

    def write_file(self, file_path):
        if not self.metadata['mime_type']:
            self.metadata['mime_type'] = 'text/plain'

        data = {}
        data['current-tab'] = self._notebook.get_current_page()
        data['tabs'] = []

        for i in range(self._notebook.get_n_pages()):
            page = self._notebook.get_nth_page(i)

            def selected_cb(terminal, c, row, cb_data):
                return 1
            scrollback_text = page.vt.get_text(selected_cb, False)

            scrollback_lines = scrollback_text.split('\n')

            # Note- this currently gets the child's initial environment
            # rather than the current environment, making it not very useful.
            environment = open('/proc/%d/environ' %
                               page.pid, 'r').read().split('\0')

            cwd = os.readlink('/proc/%d/cwd' % page.pid)

            tab_state = {'env': environment, 'cwd': cwd,
                         'scrollback': scrollback_lines}

            data['tabs'].append(tab_state)

        fd = open(file_path, 'w')
        text = simplejson.dumps(data)
        fd.write(text)
        fd.close()

    def _get_conf(self, conf, var, default):
        if conf.has_option('terminal', var):
            if isinstance(default, bool):
                return conf.getboolean('terminal', var)
            elif isinstance(default, int):
                return conf.getint('terminal', var)
            else:
                return conf.get('terminal', var)
        else:
            conf.set('terminal', var, default)

            return default

    def _configure_vt(self, vt):
        conf = ConfigParser.ConfigParser()
        conf_file = os.path.join(env.get_profile_path(), 'terminalrc')

        if os.path.isfile(conf_file):
            f = open(conf_file, 'r')
            conf.readfp(f)
            f.close()
        else:
            conf.add_section('terminal')

        font = self._get_conf(conf, 'font', 'Monospace')
        vt.set_font(pango.FontDescription(font))

        fg_color = self._get_conf(conf, 'fg_color', '#000000')
        bg_color = self._get_conf(conf, 'bg_color', '#FFFFFF')
        vt.set_colors(gtk.gdk.color_parse(fg_color),
                      gtk.gdk.color_parse(bg_color), [])

        blink = self._get_conf(conf, 'cursor_blink', False)
        vt.set_cursor_blinks(blink)

        bell = self._get_conf(conf, 'bell', False)
        vt.set_audible_bell(bell)

        scrollback_lines = self._get_conf(conf, 'scrollback_lines', 1000)
        vt.set_scrollback_lines(scrollback_lines)

        vt.set_allow_bold(True)

        scroll_key = self._get_conf(conf, 'scroll_on_keystroke', True)
        vt.set_scroll_on_keystroke(scroll_key)

        scroll_output = self._get_conf(conf, 'scroll_on_output', False)
        vt.set_scroll_on_output(scroll_output)

        emulation = self._get_conf(conf, 'emulation', 'xterm')
        vt.set_emulation(emulation)

        visible_bell = self._get_conf(conf, 'visible_bell', False)
        vt.set_visible_bell(visible_bell)

        conf.write(open(conf_file, 'w'))
