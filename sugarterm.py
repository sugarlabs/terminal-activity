# -*- coding: utf-8; -*-
"""
Copyright (C) 2007-2013 Guake authors
Copyright (c) 2020 Srevin Saju <srevin03@gmail.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301 USA

This is a modified upstream source of the famous Guake Terminal
https://github.com/Guake/guake/blob/master/guake/terminal.py

"""
import code
import logging
import os
import re
import shlex
import signal
import subprocess
import sys
import threading
import uuid

from enum import IntEnum
from pathlib import Path
from typing import Optional
from typing import Tuple
from urllib.parse import unquote
from urllib.parse import urlparse

from time import sleep

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')  # vte-0.38

from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import GdkX11
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import Vte


TERMINAL_MATCH_TAGS = ('schema', 'http', 'https', 'email', 'ftp')

# Beware this is a PRCE (Perl) regular expression, not a Python one!
# Edit: use regex101.com with PCRE syntax
TERMINAL_MATCH_EXPRS = [
    "(news:|telnet:|nntp:|file:\/|https?:|ftps?:|webcal:)\/\/([-[:alnum:]]+"
    "(:[-[:alnum:],?;.:\/!%$^\*&~\"#']+)?\@)?[-[:alnum:]]+(\.[-[:alnum:]]+)*"
    "(:[0-9]{1,5})?(\/[-[:alnum:]_$.+!*(),;:@&=?\/~#'%]*[^].> \t\r\n,\\\"])?",
    "(www|ftp)[-[:alnum:]]*\.[-[:alnum:]]+(\.[-[:alnum:]]+)*(:[0-9]{1,5})?"
    "(\/[-[:alnum:]_$.+!*(),;:@&=?\/~#%]*[^]'.>) \t\r\n,\\\"])?",
    "(mailto:)?[-[:alnum:]][-[:alnum:].]*@[-[:alnum:]]+\.[-[:alnum:]]+(\\.[-[:alnum:]]+)*"
]

log = logging

libutempter = None
try:
    # this allow to run some commands that requires libuterm to
    # be injected in current process, as: wall
    from atexit import register as at_exit_call
    from ctypes import cdll
    libutempter = cdll.LoadLibrary('libutempter.so.0')
    if libutempter is not None:
        # We absolutely need to remove the old tty from the utmp !!!
        at_exit_call(libutempter.utempter_remove_added_record)
except Exception as e:
    libutempter = None
    sys.stderr.write("[WARN] ===================================================================\n")
    sys.stderr.write("[WARN] Unable to load the library libutempter !\n")
    sys.stderr.write(
        "[WARN] Some feature might not work:\n"
        "[WARN]  - 'exit' command might freeze the terminal instead of closing the tab\n"
        "[WARN]  - the 'wall' command is known to work badly\n"
    )
    sys.stderr.write("[WARN] Error: " + str(e) + '\n')
    sys.stderr.write(
        "[WARN] ===================================================================²\n"
    )


def halt(loc):
    code.interact(local=loc)


__all__ = ['SugarTerminal']

# pylint: enable=anomalous-backslash-in-string


class DropTargets(IntEnum):
    URIS = 0
    TEXT = 1


class SugarTerminal(Vte.Terminal):
    """
    Just a vte.Terminal with some properties already set.
    """
    def __init__(self):
        super(SugarTerminal, self).__init__()

        self.add_matches()
        self.handler_ids = []
        self.handler_ids.append(self.connect('button-press-event', self.button_press))
        self.connect('child-exited', self.on_child_exited)  # Call on_child_exited, don't remove it
        self.matched_value = ''
        self.font_scale_index = 0
        self._pid = None
        # self.custom_bgcolor = None
        # self.custom_fgcolor = None
        self.found_link = None
        self.uuid = uuid.uuid4()

        # Custom colors
        self.custom_bgcolor = None
        self.custom_fgcolor = None
        self.custom_palette = None

        self.setup_drag_and_drop()

    def setup_drag_and_drop(self):
        self.targets = Gtk.TargetList()
        self.targets.add_uri_targets(DropTargets.URIS)
        self.targets.add_text_targets(DropTargets.TEXT)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.drag_dest_set_target_list(self.targets)
        self.connect('drag-data-received', self.on_drag_data_received)

    def get_uuid(self):
        return self.uuid

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, pid):
        self._pid = pid

    def feed_child(self, resolved_cmdline):
        if (Vte.MAJOR_VERSION, Vte.MINOR_VERSION) >= (0, 42):
            encoded = resolved_cmdline.encode("utf-8")
            try:
                super().feed_child_binary(encoded)
            except TypeError:
                # The doc doest not say clearly at which version the feed_child* function has lost
                # the "len" parameter :(
                super().feed_child(resolved_cmdline, len(resolved_cmdline))
        else:
            super().feed_child(resolved_cmdline, len(resolved_cmdline))

    def execute_command(self, command):
        if command[-1] != '\n':
            command += "\n"
        self.feed_child(command)

    def copy_clipboard(self):
        if self.get_has_selection():
            super(SugarTerminal, self).copy_clipboard()
        elif self.matched_value:
            log.warning('Not Implemented Sugar')

    def add_matches(self):
        """Adds all regular expressions declared in
        guake.globals.TERMINAL_MATCH_EXPRS to the terminal to make vte
        highlight text that matches them.
        """
        try:
            # NOTE: PCRE2_UTF | PCRE2_NO_UTF_CHECK | PCRE2_MULTILINE
            # reference from vte/bindings/vala/app.vala, flags = 0x40080400u
            # also ref: https://mail.gnome.org/archives/commits-list/2016-September/msg06218.html
            VTE_REGEX_FLAGS = 0x40080400
            for expr in TERMINAL_MATCH_EXPRS:
                tag = self.match_add_regex(
                    Vte.Regex.new_for_match(expr, len(expr), VTE_REGEX_FLAGS), 0
                )
                self.match_set_cursor_type(tag, Gdk.CursorType.HAND2)


        except (GLib.Error, AttributeError) as e:  # pylint: disable=catching-non-exception
            try:
                compile_flag = 0
                if (Vte.MAJOR_VERSION, Vte.MINOR_VERSION) >= (0, 44):
                    compile_flag = GLib.RegexCompileFlags.MULTILINE
                for expr in TERMINAL_MATCH_EXPRS:
                    tag = self.match_add_gregex(GLib.Regex.new(expr, compile_flag, 0), 0)
                    self.match_set_cursor_type(tag, Gdk.CursorType.HAND2)


            except GLib.Error as e:  # pylint: disable=catching-non-exception
                log.error(
                    "ERROR: PCRE2 does not seems to be enabled on your system. "
                    "Quick Edit and other Ctrl+click features are disabled. "
                    "Please update your VTE package or contact your distribution to ask "
                    "to enable regular expression support in VTE. Exception: '%s'", str(e)
                )

    def get_current_directory(self):
        directory = os.path.expanduser('~')
        if self.pid is not None:
            try:
                cwd = os.readlink("/proc/{}/cwd".format(self.pid))
            except Exception as e:
                return directory
            if os.path.exists(cwd):
                directory = cwd
        return directory

    def is_file_on_local_server(self, text) -> Tuple[Optional[Path], Optional[int], Optional[int]]:
        """Test if the provided text matches a file on local server

        Supports:
         - absolute path
         - relative path (using current working directory)
         - file:line syntax
         - file:line:colum syntax

        Args:
            text (str): candidate for file search

        Returns
            - Tuple(None, None, None) if the provided text does not match anything
            - Tuple(file path, None, None) if only a file path is found
            - Tuple(file path, linenumber, None) if line number is found
            - Tuple(file path, linenumber, columnnumber) if line and column numbers are found
        """
        lineno = None
        colno = None
        py_func = None
        # "<File>:<line>:<col>"
        m = re.compile(r"(.*)\:(\d+)\:(\d+)$").match(text)
        if m:
            text = m.group(1)
            lineno = m.group(2)
            colno = m.group(3)
        else:
            # "<File>:<line>"
            m = re.compile(r"(.*)\:(\d+)$").match(text)
            if m:
                text = m.group(1)
                lineno = m.group(2)
            else:
                # "<File>::<python_function>"
                m = re.compile(r"^(.*)\:\:([a-zA-Z0-9\_]+)$").match(text)
                if m:
                    text = m.group(1)
                    py_func = m.group(2).strip()

        def find_lineno(text, pt, lineno, py_func):
            # print("text={!r}, pt={!r}, lineno={!r}, py_func={!r}".format(text,
            #                                                              pt, lineno, py_func))
            if lineno:
                return lineno
            if not py_func:
                return
            with pt.open() as f:
                for i, line in enumerate(f.readlines()):
                    if line.startswith("def {}".format(py_func)):
                        return i + 1
                        break

        pt = Path(text)
        log.debug("checking file existance: %r", pt)
        try:
            if pt.exists():
                lineno = find_lineno(text, pt, lineno, py_func)
                log.info("File exists: %r, line=%r", pt.absolute().as_posix(), lineno)
                return (pt, lineno, colno)
            log.debug("No file found matching: %r", text)
            cwd = self.get_current_directory()
            pt = Path(cwd) / pt
            log.debug("checking file existance: %r", pt)
            if pt.exists():
                lineno = find_lineno(text, pt, lineno, py_func)
                log.info("File exists: %r, line=%r", pt.absolute().as_posix(), lineno)
                return (pt, lineno, colno)
            log.debug("file does not exist: %s", str(pt))
        except OSError:
            log.debug("not a file name: %r", text)
        return (None, None, None)

    def button_press(self, terminal, event):
        """Handles the button press event in the terminal widget. If
        any match string is caught, another application is open to
        handle the matched resource uri.
        """
        self.matched_value = ''
        if (Vte.MAJOR_VERSION, Vte.MINOR_VERSION) >= (0, 46):
            matched_string = self.match_check_event(event)
        else:
            matched_string = self.match_check(
                int(event.x / self.get_char_width()), int(event.y / self.get_char_height())
            )

        self.found_link = None

        if event.button == 1 and (event.get_state() & Gdk.ModifierType.CONTROL_MASK):
            if (Vte.MAJOR_VERSION, Vte.MINOR_VERSION) > (0, 50):
                s = self.hyperlink_check_event(event)
            else:
                s = None
            if s is not None:
                self._on_ctrl_click_matcher((s, None))
            elif matched_string and matched_string[0]:
                self._on_ctrl_click_matcher(matched_string)
        elif event.button == 3 and matched_string:
            self.found_link = self.handleTerminalMatch(matched_string)
            self.matched_value = matched_string[0]

    def on_child_exited(self, target, status, *user_data):
        if libutempter is not None:
            if self.get_pty() is not None:
                libutempter.utempter_remove_record(self.get_pty().get_fd())

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        if info == DropTargets.URIS:
            uris = data.get_uris()
            for uri in uris:
                path = Path(unquote(urlparse(uri).path))
                self.feed_child(shlex.quote(str(path.absolute())) + ' ')
        elif info == DropTargets.TEXT:
            text = data.get_text()
            if text:
                self.feed_child(text)


    def _on_ctrl_click_matcher(self, matched_string):
        value, tag = matched_string
        found_matcher = False
        log.debug("matched string: %s", matched_string)
        # First searching in additional matchers

        if not found_matcher:
            self.found_link = self.handleTerminalMatch(matched_string)
            if self.found_link:
                self.browse_link_under_cursor()

    def handleTerminalMatch(self, matched_string):
        value, tag = matched_string
        log.debug("found tag: %r, item: %r", tag, value)
        if tag in TERMINAL_MATCH_TAGS:
            if TERMINAL_MATCH_TAGS[tag] == 'schema':
                # value here should not be changed, it is right and
                # ready to be used.
                pass
            elif TERMINAL_MATCH_TAGS[tag] == 'http':
                value = 'http://%s' % value
            elif TERMINAL_MATCH_TAGS[tag] == 'https':
                value = 'https://%s' % value
            elif TERMINAL_MATCH_TAGS[tag] == 'ftp':
                value = 'ftp://%s' % value
            elif TERMINAL_MATCH_TAGS[tag] == 'email':
                value = 'mailto:%s' % value

        if value:
            return value

    def get_link_under_cursor(self):
        return self.found_link

    def browse_link_under_cursor(self):
        if not self.found_link:
            return
        log.debug("Opening link: %s", self.found_link)
        cmd = ["xdg-open", self.found_link]
        subprocess.Popen(cmd, shell=False)

    def increase_font_size(self):
        self.font_scale += 1

    def decrease_font_size(self):
        self.font_scale -= 1

    def kill(self):
        pid = self.pid
        threading.Thread(target=self.delete_shell, args=(pid, )).start()
        # start_new_thread(self.delete_shell, (pid,))

    def delete_shell(self, pid):
        """Kill the shell with SIGHUP

        NOTE: Leave it alone, DO NOT USE os.waitpid

        > sys:1: Warning: GChildWatchSource: Exit status of a child process was requested but
                 ECHILD was received by waitpid(). See the documentation of
                 g_child_watch_source_new() for possible causes.

        g_child_watch_source_new() documentation:
            https://developer.gnome.org/glib/stable/glib-The-Main-Event-Loop.html#g-child-watch-source-new

        On POSIX platforms, the following restrictions apply to this API due to limitations
        in POSIX process interfaces:
            ...
            * the application must not wait for pid to exit by any other mechanism,
              including waitpid(pid, ...) or a second child-watch source for the same pid
            ...
        For this reason, we should not call os.waitpid(pid, ...), leave it to OS
        """
        try:
            os.kill(pid, signal.SIGHUP)
        except OSError:
            pass

    def set_color_foreground(self, font_color, *args, **kwargs):
        real_fgcolor = self.custom_fgcolor if self.custom_fgcolor else font_color
        super(SugarTerminal, self).set_color_foreground(real_fgcolor, *args, **kwargs)

    def set_color_background(self, bgcolor, *args, **kwargs):
        real_bgcolor = self.custom_bgcolor if self.custom_bgcolor else bgcolor
        super(SugarTerminal, self).set_color_background(real_bgcolor, *args, **kwargs)

    def set_color_bold(self, font_color, *args, **kwargs):
        real_fgcolor = self.custom_fgcolor if self.custom_fgcolor else font_color
        super(SugarTerminal, self).set_color_bold(real_fgcolor, *args, **kwargs)

    def set_colors(self, font_color, bg_color, palette_list, *args, **kwargs):
        real_bgcolor = self.custom_bgcolor if self.custom_bgcolor else bg_color
        real_fgcolor = self.custom_fgcolor if self.custom_fgcolor else font_color
        real_palette = self.custom_palette if self.custom_palette else palette_list
        super(SugarTerminal,
              self).set_colors(real_fgcolor, real_bgcolor, real_palette, *args, **kwargs)

    def set_color_foreground_custom(self, fgcolor, *args, **kwargs):
        """Sets custom foreground color for this terminal"""
        print('set_color_foreground_custom: %s' % self.uuid)
        self.custom_fgcolor = fgcolor
        super(SugarTerminal, self).set_color_foreground(self.custom_fgcolor, *args, **kwargs)

    def set_color_background_custom(self, bgcolor, *args, **kwargs):
        """Sets custom background color for this terminal"""
        self.custom_bgcolor = bgcolor
        super(SugarTerminal, self).set_color_background(self.custom_bgcolor, *args, **kwargs)

    def reset_custom_colors(self):
        self.custom_fgcolor = None
        self.custom_bgcolor = None
        self.custom_palette = None

    @staticmethod
    def _color_to_list(color):
        """This method is used for serialization."""
        if color is None:
            return None
        return [color.red, color.green, color.blue, color.alpha]

    @staticmethod
    def _color_from_list(color_list):
        """This method is used for deserialization."""
        return Gdk.RGBA(
            red=color_list[0], green=color_list[1], blue=color_list[2], alpha=color_list[3]
        )

    def get_custom_colors_dict(self):
        """Returns dictionary of custom colors."""
        return {
            'fg_color': self._color_to_list(self.custom_fgcolor),
            'bg_color': self._color_to_list(self.custom_bgcolor),
            'palette': [self._color_to_list(col)
                        for col in self.custom_palette] if self.custom_palette else None,
        }

    def set_custom_colors_from_dict(self, colors_dict):
        if not isinstance(colors_dict, dict):
            return

        bg_color = colors_dict.get('bg_color', None)
        if isinstance(bg_color, list):
            self.custom_bgcolor = self._color_from_list(bg_color)
        else:
            self.custom_bgcolor = None

        fg_color = colors_dict.get('fg_color', None)
        if isinstance(fg_color, list):
            self.custom_fgcolor = self._color_from_list(fg_color)
        else:
            self.custom_fgcolor = None

        palette = colors_dict.get('palette', None)
        if isinstance(palette, list):
            self.custom_palette = [self._color_from_list(col) for col in palette]
        else:
            self.custom_palette = None
