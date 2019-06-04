# coding=utf-8
import gi
import os
import time

try:
    gi.require_version('Vte', '2.91')
except:
    gi.require_version('Vte', '2.90')

from gi.repository import Vte
from gi.repository import Gdk

from sugar3.datastore import datastore
from sugar3 import profile
try:
    from sugar3.activity.activity import launch_bundle
    _HAS_BUNDLE_LAUNCHER = True
except ImportError:
    _HAS_BUNDLE_LAUNCHER = False

TERMINAL_MATCH_TAGS = ['schema', 'http', 'https', 'email', 'ftp']

TERMINAL_MATCH_EXPRS = [
    "(news:|telnet:|nntp:|file:\/|https?:|ftps?:|webcal:)\/\/([-[:alnum:]]+"
    "(:[-[:alnum:],?;.:\/!%$^\*&~\"#']+)?\@)?[-[:alnum:]]+(\.[-[:alnum:]]+)*"
    "(:[0-9]{1,5})?(\/[-[:alnum:]_$.+!*(),;:@&=?\/~#'%]*[^].> \t\r\n,\\\"])?",
    "(www|ftp)[-[:alnum:]]*\.[-[:alnum:]]+(\.[-[:alnum:]]+)*(:[0-9]{1,5})?"
    "(\/[-[:alnum:]_$.+!*(),;:@&=?\/~#%]*[^]'.>) \t\r\n,\\\"])?",
    "(mailto:)?[-[:alnum:]][-[:alnum:].]*@[-[:alnum:]]+\.[-[:alnum:]]+(\\.[-[:alnum:]]+)*",
    "HtTp://déjà-vu.com:10000/déjà/vu",
    "HTTP://joe:sEcReT@➡.ws:1080",
    "https://cömbining-áccents",
    "https://[dead::beef]:12345/ipv6",
    "https://[dead::beef:11.22.33.44]",
    "https://dead",
    "http://[dead::beef:111.222.333.444]",
    "http://safeguy:!#$%^&*@host",
    "http://dudewithnopassword:@example.com",
    "http://invalidusername!@host",
    "http://ab.cd/ef?g=h&i=j|k=l#m=n:o=p",
]


class Terminal(Vte.Terminal):
    """ A Vte.Terminal with some properties set """

    def __init__(self, activity):
        super(Terminal, self).__init__()
        self.activity = activity
        self.connect('button-press-event', self._button_press)
        if (Vte.MAJOR_VERSION, Vte.MINOR_VERSION) >= (0, 50):
            self.set_allow_hyperlink(True)
        self.check_matches()
        self.matched_value = ''
        self.found_link = None

    def check_matches(self):
        for expr in TERMINAL_MATCH_EXPRS:
            regex = Vte.Regex.new_for_match(expr, len(expr), 0)
            tag = self.match_add_regex(
                regex, 0
            )
            self.match_set_cursor_name(tag, "pointer")

    def _button_press(self, terminal, event):
        self.matched_value = ''
        if (Vte.MAJOR_VERSION, Vte.MINOR_VERSION) >= (0, 46):
            matched_string = self.match_check_event(event)
        else:
            matched_string = self.match_check(
                int(event.x / self.get_char_width()), \
                    int(event.y / self.get_char_height())
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
        path = os.path.join(self.activity.get_activity_root(), 'instance', '%i' % time.time())
        self.create_journal_entry(path, self.found_link)

    def create_journal_entry(self, path, URL):
        fd = open(path, "w+")
        fd.write(URL)
        fd.close()
        journal_entry = datastore.create()
        journal_entry.metadata['title'] = 'Browse Activity'
        journal_entry.metadata['title_set_by_user'] = '1'
        journal_entry.metadata['keep'] = '0'
        journal_entry.metadata['mime_type'] = 'text/uri-list'
        journal_entry.metadata['icon-color'] = profile.get_color().to_string()
        journal_entry.metadata['description'] = "This is the URL opening of " + URL
        journal_entry.file_path = path
        datastore.write(journal_entry)
        self._object_id = journal_entry.object_id
        launch_bundle(object_id=self._object_id)
