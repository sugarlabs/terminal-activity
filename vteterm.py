# Tie up everything and the lose ends as per guake
import os
import sys
import logging
from gettext import gettext as _
import subprocess
import gi

try:
    gi.require_version('Vte', '2.91')
except:
    gi.require_version('Vte', '2.90')

from gi.repository import Vte
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gdk

VTE_VERSION = 0
try:
    VTE_VERSION = Vte.MINOR_VERSION
except:
    # version is not published in old versions of vte
    pass

TERMINAL_MATCH_TAGS = ['schema', 'http', 'https', 'email', 'ftp']

class Terminal(Vte.Terminal):
    """ A Vte.Terminal with some properties set """

    def __init__(self, activity):
        super(Terminal, self).__init__()
        self.activity = activity
        self.handler_ids = []
        self.handler_ids.append(self.connect('button-press-event', self._button_press))
    
        if (Vte.MAJOR_VERSION, Vte.MINOR_VERSION) >= (0, 50):
            self.set_allow_hyperlink(True)
    
        self.matched_value = ''
        self.found_link = None

    def _button_press(self, terminal, event):
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

    def _on_ctrl_click_matcher(self, matched_string):
        self.found_link = self.handleTerminalMatch(matched_string)
        if self.found_link:
            self.browse_link_under_cursor()

    def handleTerminalMatch(self, matched_string):
        value, tag = matched_string
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

    def browse_link_under_cursor(self):
        if not self.found_link:
            return
        cmd = ["xdg-open", self.found_link]
        subprocess.Popen(cmd, shell=False)  # Here is where the activity call is being made
        
        