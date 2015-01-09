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
import json
import ConfigParser
import logging
from gettext import gettext as _

from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Vte
from gi.repository import Pango

from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton

from sugar3.activity.widgets import EditToolbar
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.activity import activity
from sugar3 import env

from widgets import BrowserNotebook
from widgets import TabLabel

from helpbutton import HelpButton


MASKED_ENVIRONMENT = [
    'DBUS_SESSION_BUS_ADDRESS',
    'PPID']

log = logging.getLogger('Terminal')
log.setLevel(logging.DEBUG)
logging.basicConfig()

ZOOM_STEP = 1024

VTE_VERSION = 0
try:
    VTE_VERSION = Vte.MINOR_VERSION
except:
    # version is not published in old versions of vte
    pass


class TerminalActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        # HACK to avoid Escape key disable fullscreen mode on Terminal Activity
        # This is related with http://bugs.sugarlabs.org/ticket/440
        self.disconnect_by_func(self._Window__key_press_cb)
        self.connect('key-press-event', self.__key_press_cb)

        self.max_participants = 1

        self._theme_state = "light"

        toolbar_box = ToolbarBox()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        edit_toolbar = self._create_edit_toolbar()
        edit_toolbar_button = ToolbarButton(
            page=edit_toolbar,
            icon_name='toolbar-edit'
        )
        edit_toolbar.show()
        toolbar_box.toolbar.insert(edit_toolbar_button, -1)
        edit_toolbar_button.show()

        view_toolbar = self._create_view_toolbar()
        view_toolbar_button = ToolbarButton(
            page=view_toolbar,
            icon_name='toolbar-view')
        view_toolbar.show()
        toolbar_box.toolbar.insert(view_toolbar_button, -1)
        view_toolbar_button.show()

        self._delete_tab_toolbar = None
        self._previous_tab_toolbar = None
        self._next_tab_toolbar = None

        helpbutton = self._create_help_button()
        toolbar_box.toolbar.insert(helpbutton, -1)
        helpbutton.show_all()

        separator = Gtk.SeparatorToolItem()
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

        self._notebook = BrowserNotebook()
        self._notebook.connect("tab-added", self.__open_tab_cb)
        self._notebook.set_property("tab-pos", Gtk.PositionType.TOP)
        self._notebook.set_scrollable(True)
        self._notebook.show()

        self.set_canvas(self._notebook)

        self._create_tab(None)

    def _create_edit_toolbar(self):
        edit_toolbar = EditToolbar()
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

    def _toggled_theme(self, button):
        if self._theme_state == "dark":
            self._theme_state = "light"
        elif self._theme_state == "light":
            self._theme_state = "dark"
        self._update_theme()

    def _update_theme(self):
        if self._theme_state == "light":
            self._theme_toggler.set_icon_name('dark-theme')
            self._theme_toggler.set_tooltip('Switch to Dark Theme')
        elif self._theme_state == "dark":
            self._theme_toggler.set_icon_name('light-theme')
            self._theme_toggler.set_tooltip('Switch to Light Theme')

        for i in range(self._notebook.get_n_pages()):
            vt = self._notebook.get_nth_page(i).vt
            self._configure_vt(vt)

    def _create_view_toolbar(self):  # Color changer and Zoom toolbar
        view_toolbar = Gtk.Toolbar()

        self._theme_toggler = ToolButton('dark-theme')
        self._theme_toggler.set_tooltip('Switch to Dark Theme')
        self._theme_toggler.connect('clicked', self._toggled_theme)
        view_toolbar.insert(self._theme_toggler, -1)
        self._theme_toggler.show()

        sep = Gtk.SeparatorToolItem()
        view_toolbar.insert(sep, -1)
        sep.show()

        zoom_out_button = ToolButton('zoom-out')
        zoom_out_button.set_tooltip(_('Zoom out'))
        zoom_out_button.props.accelerator = '<Ctrl>minus'
        zoom_out_button.connect('clicked', self.__zoom_out_cb)
        view_toolbar.insert(zoom_out_button, -1)
        zoom_out_button.show()

        zoom_in_button = ToolButton('zoom-in')
        zoom_in_button.set_tooltip(_('Zoom in'))
        zoom_in_button.props.accelerator = '<Ctrl>plus'
        zoom_in_button.connect('clicked', self.__zoom_in_cb)
        view_toolbar.insert(zoom_in_button, -1)
        zoom_in_button.show()

        fullscreen_button = ToolButton('view-fullscreen')
        fullscreen_button.set_tooltip(_("Fullscreen"))
        fullscreen_button.props.accelerator = '<Alt>Return'
        fullscreen_button.connect('clicked', self.__fullscreen_cb)
        view_toolbar.insert(fullscreen_button, -1)
        fullscreen_button.show()
        return view_toolbar

    def _zoom(self, step):
        current_page = self._notebook.get_current_page()
        vt = self._notebook.get_nth_page(current_page).vt
        font_desc = vt.get_font()
        font_desc.set_size(font_desc.get_size() + step)
        vt.set_font(font_desc)

    def __zoom_out_cb(self, button):
        self._zoom(ZOOM_STEP * -1)

    def __zoom_in_cb(self, button):
        self._zoom(ZOOM_STEP)

    def __fullscreen_cb(self, button):
        self.fullscreen()

    def _create_help_button(self):
        helpitem = HelpButton()

        helpitem.add_section(_('Useful commands'))
        helpitem.add_section(_('cd'))
        helpitem.add_paragraph(_('Change directory'))
        helpitem.add_paragraph(_('To use it, write: cd directory'))
        helpitem.add_paragraph(
            _('If you call it without parameters, will change\n'
                'to the user directory'))
        helpitem.add_section(_('ls'))
        helpitem.add_paragraph(_('List the content of a directory.'))
        helpitem.add_paragraph(_('To use it, write: ls directory'))
        helpitem.add_paragraph(
            _('If you call it without parameters, will list the\n'
                'working directory'))
        helpitem.add_section(_('cp'))
        helpitem.add_paragraph(_('Copy a file to a specific location'))
        helpitem.add_paragraph(_('Call it with the file and the new location'))
        helpitem.add_paragraph(_('Use: cp file directory'))
        helpitem.add_section(_('rm'))
        helpitem.add_paragraph(_('Removes a file in any path'))
        helpitem.add_paragraph(_('Use: rm file'))
        helpitem.add_section(_('su'))
        helpitem.add_paragraph(_('Login as superuser (root)'))
        helpitem.add_paragraph(
            _('The root user is the administrator of the\nsystem'))
        helpitem.add_paragraph(
            _('You must be careful, because you can modify\nsystem files'))

        return helpitem

    def __open_tab_cb(self, btn):
        index = self._create_tab(None)
        self._notebook.page = index
        if self._notebook.get_n_pages() == 2:
            self._notebook.get_tab_label(
                self._notebook.get_nth_page(0)).show_close_button()

    def __close_tab_cb(self, btn, child):
        index = self._notebook.page_num(child)
        self._close_tab(index)
        if self._notebook.get_n_pages() == 1:
            self._notebook.get_tab_label(
                self._notebook.get_nth_page(0)).hide_close_button()

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
        widget.feed_child(selection.get_text(), -1)
        context.finish(True, False, time)
        return True

    def _create_tab(self, tab_state):
        vt = Vte.Terminal()
        vt.connect("child-exited", self.__tab_child_exited_cb)
        vt.connect("window-title-changed", self.__tab_title_changed_cb)

        # FIXME have to resend motion events to parent, see #1402
        vt.connect('motion-notify-event', self.__motion_notify_cb)

        vt.drag_dest_set(Gtk.DestDefaults.MOTION | Gtk.DestDefaults.DROP,
                         [Gtk.TargetEntry.new('text/plain', 0, 0),
                          Gtk.TargetEntry.new('STRING', 0, 1)],
                         Gdk.DragAction.DEFAULT | Gdk.DragAction.COPY)
        vt.drag_dest_add_text_targets()
        vt.connect('drag_data_received', self.__drag_data_received_cb)

        self._configure_vt(vt)

        vt.show()

        scrollbar = Gtk.VScrollbar.new(vt.get_vadjustment())

        box = Gtk.HBox()
        box.pack_start(vt, True, True, 0)
        box.pack_start(scrollbar, False, True, 0)

        box.vt = vt
        box.show()

        tablabel = TabLabel(box)
        tablabel.connect('tab-close', self.__close_tab_cb)
        tablabel.update_size(200)
        box.label = tablabel

        index = self._notebook.append_page(box, tablabel)
        tablabel.show_all()

        # Uncomment this to only show the tab bar when there is at least
        # one tab. I think it's useful to always see it, since it displays
        # the 'window title'.
        # self._notebook.props.show_tabs = self._notebook.get_n_pages() > 1
        tablabel.hide_close_button() if self._notebook.get_n_pages() == 1\
            else None
        self._notebook.show_all()

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

            if 'font_size' in tab_state:
                font_desc = vt.get_font()
                font_desc.set_size(tab_state['font_size'])
                vt.set_font(font_desc)

            # Restore the scrollback buffer.
            for l in tab_state['scrollback']:
                vt.feed(str(l) + '\r\n')

        if hasattr(vt, 'fork_command_full'):
            sucess_, box.pid = vt.fork_command_full(
                Vte.PtyFlags.DEFAULT, os.environ["HOME"],
                ["/bin/bash"], [], GLib.SpawnFlags. DO_NOT_REAP_CHILD,
                None, None)
        else:
            sucess_, box.pid = vt.spawn_sync(
                Vte.PtyFlags.DEFAULT, os.environ["HOME"],
                ["/bin/bash"], [], GLib.SpawnFlags. DO_NOT_REAP_CHILD,
                None, None)

        self._notebook.props.page = index
        vt.grab_focus()

        return index

    def __motion_notify_cb(self, widget, event):
        self.emit('motion-notify-event', Gdk.Event(event))

    def __key_press_cb(self, window, event):
        """Route some keypresses directly to the vte and then drop them.

        This prevents Sugar from hijacking events that are useful in
        the vte.

        """

        def event_to_vt(event):
            current_page = self._notebook.get_current_page()
            vt = self._notebook.get_nth_page(current_page).vt
            vt.event(event)

        key_name = Gdk.keyval_name(event.keyval)

        # Escape is used in Sugar to cancel fullscreen mode.
        if key_name == 'Escape':
            event_to_vt(event)
            return True

        elif event.get_state() & Gdk.ModifierType.CONTROL_MASK:
            if key_name in ['z', 'q']:
                event_to_vt(event)
                return True
            elif key_name == 'Tab':
                current_index = self._notebook.get_current_page()
                if current_index == self._notebook.get_n_pages() - 1:
                    self._notebook.set_current_page(0)
                else:
                    self._notebook.set_current_page(current_index + 1)
                return True
            elif event.get_state() & Gdk.ModifierType.SHIFT_MASK:
                if key_name == 'ISO_Left_Tab':
                    current_index = self._notebook.get_current_page()
                    if current_index == 0:
                        self._notebook.set_current_page(
                            self._notebook.get_n_pages() - 1)
                    else:
                        self._notebook.set_current_page(current_index - 1)
                    return True
                elif key_name == 'T':
                    self._create_tab(None)
                    return True

        return False

    def read_file(self, file_path):
        if self.metadata['mime_type'] != 'text/plain':
            return

        fd = open(file_path, 'r')
        text = fd.read()
        data = json.loads(text)
        fd.close()

        # Clean out any existing tabs.
        while self._notebook.get_n_pages():
            self._notebook.remove_page(0)

        # Restore theme
        self._theme_state = data['theme']
        self._update_theme()

        # Create new tabs from saved state.
        for tab_state in data['tabs']:
            self._create_tab(tab_state)

        # Restore active tab.
        self._notebook.props.page = data['current-tab']

        # Create a blank one if this state had no terminals.
        if self._notebook.get_n_pages() == 0:
            self._create_tab(None)

    def write_file(self, file_path):
        if not self.metadata['mime_type']:
            self.metadata['mime_type'] = 'text/plain'

        data = {}
        data['current-tab'] = self._notebook.get_current_page()
        data['theme'] = self._theme_state
        data['tabs'] = []

        for i in range(self._notebook.get_n_pages()):

            def is_selected(vte, *args):
                return True

            page = self._notebook.get_nth_page(i)

            text = ''
            if VTE_VERSION >= 38:
                # in older versions of vte, get_text() makes crash
                # the activity at random - SL #4627
                try:
                    # get_text is only available in latest vte #676999
                    # and pygobject/gobject-introspection #690041
                    text, attr_ = page.vt.get_text(is_selected, None)
                except AttributeError:
                    pass

            scrollback_lines = text.split('\n')

            # Note- this currently gets the child's initial environment
            # rather than the current environment, making it not very useful.
            environment = open('/proc/%d/environ' %
                               page.pid, 'r').read().split('\0')

            cwd = os.readlink('/proc/%d/cwd' % page.pid)

            font_desc = page.vt.get_font()

            tab_state = {'env': environment, 'cwd': cwd,
                         'font_size': font_desc.get_size(),
                         'scrollback': scrollback_lines}

            data['tabs'].append(tab_state)

        fd = open(file_path, 'w')
        text = json.dumps(data)
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
        vt.set_font(Pango.FontDescription(font))

        self._theme_colors = {"light": {'fg_color': '#000000',
                                        'bg_color': '#FFFFFF'},
                              "dark": {'fg_color': '#FFFFFF',
                                       'bg_color': '#000000'}}
        fg_color = self._theme_colors[self._theme_state]['fg_color']
        bg_color = self._theme_colors[self._theme_state]['bg_color']
        try:
            vt.set_colors(Gdk.color_parse(fg_color),
                          Gdk.color_parse(bg_color), [])
        except TypeError:
            # Vte 0.38 requires the colors set as a different type
            # in Fedora 21 we get a exception
            # TypeError: argument foreground: Expected Gdk.RGBA,
            # but got gi.overrides.Gdk.Color
            vt.set_colors(Gdk.RGBA(*Gdk.color_parse(fg_color).to_floats()),
                          Gdk.RGBA(*Gdk.color_parse(bg_color).to_floats()), [])

        blink = self._get_conf(conf, 'cursor_blink', False)
        vt.set_cursor_blink_mode(blink)

        bell = self._get_conf(conf, 'bell', False)
        vt.set_audible_bell(bell)

        scrollback_lines = self._get_conf(conf, 'scrollback_lines', 1000)
        vt.set_scrollback_lines(scrollback_lines)

        vt.set_allow_bold(True)

        scroll_key = self._get_conf(conf, 'scroll_on_keystroke', True)
        vt.set_scroll_on_keystroke(scroll_key)

        scroll_output = self._get_conf(conf, 'scroll_on_output', False)
        vt.set_scroll_on_output(scroll_output)

        if hasattr(vt, 'set_emulation'):
            # set_emulation is not available after vte commit
            # 4e253be9282829f594c8a55ca08d1299e80e471d
            emulation = self._get_conf(conf, 'emulation', 'xterm')
            vt.set_emulation(emulation)

        if hasattr(vt, 'set_visible_bell'):
            visible_bell = self._get_conf(conf, 'visible_bell', False)
            vt.set_visible_bell(visible_bell)

        conf.write(open(conf_file, 'w'))
