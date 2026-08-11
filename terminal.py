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
import logging
from gettext import gettext as _


def _parse_rgba(hex_str):
    rgba = Gdk.RGBA()
    rgba.parse(hex_str)
    return rgba


import gi


vs = {'Gtk': '4.0'}
for api, ver in vs.items():
    gi.require_version(api, ver)

gi.require_version('Vte', '3.91')

from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Vte
from gi.repository import Pango

from sugar4.graphics.toolbutton import ToolButton
from sugar4.graphics.toolbarbox import ToolbarBox
from sugar4.graphics.toolbarbox import ToolbarButton

from sugar4.activity.widgets import EditToolbar
from sugar4.activity.widgets import ActivityToolbarButton
from sugar4.activity.widgets import StopButton
from sugar4.activity import activity
from sugar4.graphics.colorbutton import ColorToolButton, get_svg_color_string

from widgets import BrowserNotebook
from widgets import TabLabel

from helpbutton import HelpButton
from sugarterm import SugarTerminal

MASKED_ENVIRONMENT = [
    'DBUS_SESSION_BUS_ADDRESS',
    'PPID']

log = logging.getLogger('Terminal')
log.setLevel(logging.DEBUG)
logging.basicConfig()

try:
    olpc_build = open('/boot/olpc_build', 'r').readline()
except Exception:
    olpc_build = ''

if olpc_build.startswith('13'):
    FONT_SIZE = 8
else:
    FONT_SIZE = 12

VTE_VERSION = 0
try:
    VTE_VERSION = Vte.MINOR_VERSION
except Exception:
    # version is not published in old versions of vte
    pass


class TerminalActivity(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        key_controller = Gtk.EventControllerKey.new()
        key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        key_controller.connect('key-pressed', self.__key_press_cb)
        self.add_controller(key_controller)
        self.vt = None
        self.max_participants = 1
        self._theme_colors = {"light": {'fg_color': '#000000',
                                        'bg_color': '#FFFFFF'},
                              "dark": {'fg_color': '#FFFFFF',
                                       'bg_color': '#000000'},
                              "custom": {'fg_color': '#000000',
                                         'bg_color': '#FFFFFF'}
                              }
        self._theme_state = "light"

        self._font_size = FONT_SIZE
        self.build_notebook()
        self.build_toolbar()

    def build_notebook(self):
        self._notebook = BrowserNotebook()
        self._notebook.connect("tab-added", self.__open_tab_cb)
        self._notebook.set_property("tab-pos", Gtk.PositionType.TOP)
        self._notebook.set_scrollable(True)
        self._notebook.set_visible(True)
        self.set_canvas(self._notebook)
        self._create_tab(None)

    def build_toolbar(self):
        toolbar_box = ToolbarBox()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.prepend(activity_button)
        activity_button.set_visible(True)

        edit_toolbar = self._create_edit_toolbar()
        edit_toolbar_button = ToolbarButton(
            page=edit_toolbar,
            icon_name='toolbar-edit'
        )
        edit_toolbar.set_visible(True)
        toolbar_box.toolbar.append(edit_toolbar_button)
        edit_toolbar_button.set_visible(True)

        view_toolbar = self._create_view_toolbar()
        view_toolbar_button = ToolbarButton(
            page=view_toolbar,
            icon_name='toolbar-view')
        view_toolbar.set_visible(True)
        toolbar_box.toolbar.append(view_toolbar_button)
        view_toolbar_button.set_visible(True)

        self._delete_tab_toolbar = None
        self._previous_tab_toolbar = None
        self._next_tab_toolbar = None

        helpbutton = self._create_help_button()
        toolbar_box.toolbar.append(helpbutton)
        helpbutton.set_visible(True)

        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        separator.set_hexpand(True)
        separator.set_opacity(0.0)
        toolbar_box.toolbar.append(separator)
        separator.set_visible(True)

        stop_button = StopButton(self)
        stop_button.props.accelerator = '<Ctrl><Shift>Q'
        toolbar_box.toolbar.append(stop_button)
        stop_button.set_visible(True)

        self.set_toolbar_box(toolbar_box)
        toolbar_box.set_visible(True)

    def fullscreen(self):
        self._notebook.set_show_tabs(False)
        activity.Activity.fullscreen(self)

    def unfullscreen(self):
        self._notebook.set_show_tabs(True)
        activity.Activity.unfullscreen(self)

    def _create_edit_toolbar(self):
        edit_toolbar = EditToolbar()
        edit_toolbar.undo.props.visible = False
        edit_toolbar.redo.props.visible = False
        edit_toolbar.separator.props.visible = False
        edit_toolbar.copy.connect('clicked', self.__copy_cb)
        edit_toolbar.copy.props.accelerator = '<Ctrl><Shift>C'
        edit_toolbar.paste.connect('clicked', self.__paste_cb)
        edit_toolbar.paste.props.accelerator = '<Ctrl><Shift>V'

        clear = ToolButton('edit-clear')
        clear.set_tooltip(_('Clear scrollback'))
        clear.connect('clicked', self.__clear_cb)
        edit_toolbar.append(clear)
        clear.set_visible(True)
        return edit_toolbar

    def __copy_cb(self, button):
        vt = self._notebook.get_nth_page(self._notebook.get_current_page()).vt
        if vt.get_has_selection():
            vt.copy_clipboard_format(Vte.Format.TEXT)

    def __paste_cb(self, button):
        vt = self._notebook.get_nth_page(self._notebook.get_current_page()).vt
        vt.paste_clipboard()

    def __bg_color_notify_cb(self, button, pspec):
        color = button.get_color()
        self._theme_state = 'custom'
        self._theme_colors['custom']['bg_color'] = get_svg_color_string(color)
        self._update_theme()

    def __fg_color_notify_cb(self, button, pspec):
        color = button.get_color()
        self._theme_state = 'custom'
        self._theme_colors['custom']['fg_color'] = get_svg_color_string(color)
        self._update_theme()

    def _update_custom_theme(self, fg_color, bg_color):
        self._theme_colors['custom']['fg_color'] = fg_color
        self._theme_colors['custom']['bg_color'] = bg_color

    def _toggled_theme(self, button):
        if self._theme_state == "dark":
            self._theme_state = "light"
        elif self._theme_state == "light":
            self._theme_state = "dark"
        else:
            if button.get_icon_name() == "light-theme" or \
                    self._theme_colors['custom'] == \
                    self._theme_colors['dark']:
                self._theme_state = "light"
            else:
                self._theme_state = "dark"
        previous_theme = self._theme_colors[self._theme_state]
        self._update_custom_theme(
            previous_theme['fg_color'], previous_theme['bg_color'])
        self._update_theme()

    def _update_theme(self):
        if self._theme_state == "light":
            self._theme_toggler.set_icon_name('dark-theme')
            self._theme_toggler.set_tooltip('Switch to Dark Theme')
        elif self._theme_state == "dark":
            self._theme_toggler.set_icon_name('light-theme')
            self._theme_toggler.set_tooltip('Switch to Light Theme')
        else:
            # If custom color is dark, update the theme toggler
            if self._theme_colors['custom'] == self._theme_colors['dark']:
                self._theme_toggler.set_icon_name('light-theme')
                self._theme_toggler.set_tooltip('Switch to Light Theme')

        for i in range(self._notebook.get_n_pages()):
            vt = self._notebook.get_nth_page(i).vt
            vt.set_term_colors(self._theme_colors['custom'])

    def _create_view_toolbar(self):  # Color changer and Zoom toolbar
        view_toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self._theme_toggler = ToolButton('dark-theme')
        self._theme_toggler.set_tooltip('Switch to Dark Theme')
        self._theme_toggler.props.accelerator = '<Ctrl><Shift>I'
        self._theme_toggler.connect('clicked', self._toggled_theme)
        view_toolbar.append(self._theme_toggler)
        self._theme_toggler.set_visible(True)

        self.fg_color_palette = ColorToolButton('color-preview')
        self.fg_color_palette._tooltip = "Set Foreground Text color"
        self.fg_color_palette.set_title('Foreground Color')
        self.fg_color_palette.connect(
            'notify::color', self.__fg_color_notify_cb)
        view_toolbar.append(self.fg_color_palette)
        self.fg_color_palette.set_visible(True)

        self.bg_color_palette = ColorToolButton('color-preview')
        self.bg_color_palette._tooltip = "Set Background color"
        self.bg_color_palette.set_title('Background Color')
        self.bg_color_palette.connect(
            'notify::color', self.__bg_color_notify_cb)
        self.bg_color_palette.set_color(_parse_rgba('#FFFFFF'))
        view_toolbar.append(self.bg_color_palette)
        self.bg_color_palette.set_visible(True)

        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        view_toolbar.append(sep)
        sep.set_visible(True)

        zoom_out_button = ToolButton('zoom-out')
        zoom_out_button.set_tooltip(_('Zoom out'))
        zoom_out_button.props.accelerator = '<Ctrl>minus'
        zoom_out_button.connect('clicked', self.__zoom_out_cb)
        view_toolbar.append(zoom_out_button)
        zoom_out_button.set_visible(True)

        zoom_in_button = ToolButton('zoom-in')
        zoom_in_button.set_tooltip(_('Zoom in'))
        zoom_in_button.props.accelerator = '<Ctrl>plus'
        zoom_in_button.connect('clicked', self.__zoom_in_cb)
        view_toolbar.append(zoom_in_button)
        zoom_in_button.set_visible(True)

        fullscreen_button = ToolButton('view-fullscreen')
        fullscreen_button.set_tooltip(_("Fullscreen"))
        fullscreen_button.props.accelerator = '<Alt>Return'
        fullscreen_button.connect('clicked', self.__fullscreen_cb)
        view_toolbar.append(fullscreen_button)
        fullscreen_button.set_visible(True)
        return view_toolbar

    def _zoom(self, step):

        current_page = self._notebook.get_current_page()
        vt = self._notebook.get_nth_page(current_page).vt
        font_desc = vt.get_font()
        font_desc.set_size(font_desc.get_size() + Pango.SCALE * step)
        vt.set_font(font_desc)

    def __zoom_out_cb(self, button):
        self._zoom(-1)

    def __zoom_in_cb(self, button):
        self._zoom(1)

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
        vt = self._notebook.get_nth_page(self._notebook.get_current_page()).vt
        font_desc = vt.get_font()
        self._font_size = font_desc.get_size() / Pango.SCALE

        index = self._create_tab(None)
        self._notebook.page = index

    def __close_tab_cb(self, btn, child):
        index = self._notebook.page_num(child)
        self._close_tab(index)

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
        if self._notebook.get_n_pages() == 1:
            self._notebook.get_tab_label(
                self._notebook.get_nth_page(0)).hide_close_button()

    def __tab_child_exited_cb(self, vt, status=None):
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

    def _create_tab(self, tab_state):
        vt = SugarTerminal(self)
        vt.connect("child-exited", self.__tab_child_exited_cb)
        vt.connect("window-title-changed", self.__tab_title_changed_cb)

        # Handled by sugarterm setup_drag_and_drop

        vt.set_term_colors(self._theme_colors['custom'])

        vt.set_visible(True)

        scrollbar = Gtk.Scrollbar(
            orientation=Gtk.Orientation.VERTICAL,
            adjustment=vt.get_vadjustment()
        )

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        vt.set_hexpand(True)
        vt.set_vexpand(True)
        box.append(vt)
        box.append(scrollbar)

        box.vt = vt
        box.pid = -1
        box.set_visible(True)

        tablabel = TabLabel(box)
        tablabel.connect('tab-close', self.__close_tab_cb)
        tablabel.update_size(200)
        box.label = tablabel

        index = self._notebook.append_page(box, tablabel)
        tablabel.set_visible(True)

        # Uncomment this to only show the tab bar when there is at least
        # one tab. I think it's useful to always see it, since it displays
        # the 'window title'.
        # self._notebook.props.show_tabs = self._notebook.get_n_pages() > 1
        if self._notebook.get_n_pages() == 1:
            tablabel.hide_close_button()
        if self._notebook.get_n_pages() == 2:
            self._notebook.get_tab_label(
                self._notebook.get_nth_page(0)).show_close_button()
        self._notebook.set_visible(True)

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
                except Exception:
                    # ACLs may deny access
                    sys.stdout.write("Could not chdir to " + tab_state['cwd'])

            if 'font_size' in tab_state:
                font_desc = vt.get_font()
                font_desc.set_size(tab_state['font_size'])
                vt.set_font(font_desc)

            # Restore the scrollback buffer.
            for line in tab_state['scrollback']:
                vt.feed(line.encode('utf-8') + b'\r\n')

        argv = [os.environ.get('SHELL') or '/bin/bash']
        envv = ['SUGAR_TERMINAL_VERSION=%s' %
                os.environ['SUGAR_BUNDLE_VERSION']]

        saved = {}
        for name in ['SUGAR_BUNDLE_PATH', 'SUGAR_ACTIVITY_ROOT',
                     'SUGAR_BUNDLE_ID', 'SUGAR_BUNDLE_NAME',
                     'SUGAR_BUNDLE_VERSION']:
            if name in os.environ:
                saved[name] = os.environ[name]
                del os.environ[name]

        def on_spawn_cb(terminal, pid, error, box):
            if error is None:
                box.pid = pid
                terminal.pid = pid

        vt.spawn_async(
            Vte.PtyFlags.DEFAULT,
            os.environ["HOME"],
            argv,
            envv,
            GLib.SpawnFlags.DEFAULT,
            None, None,
            -1,
            None,
            on_spawn_cb,
            box
        )

        for name in saved:
            os.environ[name] = saved[name]

        self._notebook.props.page = index
        vt.grab_focus()

        return index

    def __key_press_cb(self, controller, keyval, keycode, state):
        key_name = Gdk.keyval_name(keyval)
        page = self._notebook.get_nth_page(self._notebook.get_current_page())
        if page is None:
            return False
        vt = page.vt

        # HACK to avoid Escape key disable fullscreen mode on
        # Terminal Activity and prevent Sugar from hijacking
        # Ctrl+Z/Ctrl+Q useful in the terminal.
        if key_name == 'Escape':
            controller.forward(vt)
            return True

        if state & Gdk.ModifierType.CONTROL_MASK:
            if key_name in ('z', 'q'):
                controller.forward(vt)
                return True

            if key_name == 'Tab':
                current_index = self._notebook.get_current_page()
                if current_index == self._notebook.get_n_pages() - 1:
                    self._notebook.set_current_page(0)
                else:
                    self._notebook.set_current_page(current_index + 1)
                return True
            elif state & Gdk.ModifierType.SHIFT_MASK:
                if key_name == 'ISO_Left_Tab':
                    current_index = self._notebook.get_current_page()
                    if current_index == 0:
                        self._notebook.set_current_page(
                            self._notebook.get_n_pages() - 1)
                    else:
                        self._notebook.set_current_page(current_index - 1)
                    return True
                elif key_name in ('T', 't'):
                    self._create_tab(None)
                    return True
                elif key_name in ('C', 'c'):
                    self.__copy_cb(None)
                    return True
                elif key_name in ('V', 'v'):
                    self.__paste_cb(None)
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
        if data['theme'] == 'custom':
            self._theme_colors['custom'] = data['theme_hex']
        else:
            self._theme_colors['custom'] = self._theme_colors[data['theme']]
        self.fg_color_palette.set_color(
            _parse_rgba(self._theme_colors['custom']['fg_color']))
        self.bg_color_palette.set_color(
            _parse_rgba(self._theme_colors['custom']['bg_color']))
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
        # make sures this doesn't conflict with older terminal version
        data['theme'] = 'custom'
        data['theme_hex'] = self._theme_colors['custom']
        data['tabs'] = []

        for i in range(self._notebook.get_n_pages()):

            def is_selected(vte, *args):
                return True

            page = self._notebook.get_nth_page(i)

            text = ''
            if VTE_VERSION >= 76:
                # Use get_text with format for Vte version 0.76 and above
                text = page.vt.get_text_format(Vte.Format.TEXT)
            elif VTE_VERSION >= 38:
                # in older versions of vte, get_text() makes crash
                # the activity at random - SL #4627
                try:
                    # get_text is only available in latest vte #676999
                    # and pygobject/gobject-introspection #690041
                    text, attr_ = page.vt.get_text(is_selected, None)
                except AttributeError:
                    text = ''

            scrollback_lines = text.split('\n')

            environ_file = '/proc/%d/environ' % page.pid
            if os.path.isfile(environ_file):
                # Note- this currently gets the child's initial environment
                # rather than the current environment,
                # making it not very useful.
                environment = open(environ_file, 'r').read().split('\0')

                cwd = os.readlink('/proc/%d/cwd' % page.pid)
            else:
                # terminal killed by the user
                environment = []
                cwd = '~'

            font_desc = page.vt.get_font()

            tab_state = {'env': environment, 'cwd': cwd,
                         'font_size': font_desc.get_size(),
                         'scrollback': scrollback_lines}

            data['tabs'].append(tab_state)

        with open(file_path, 'w') as fd:
            text = json.dumps(data)
            fd.write(text)

    def __clear_cb(self, button):
        vt = self._notebook.get_nth_page(self._notebook.get_current_page()).vt
        n = vt.props.scrollback_lines
        vt.set_scrollback_lines(0)
        vt.set_scrollback_lines(n)
