from gettext import gettext as _
import os
from gi.repository import Gtk, Gdk, GObject, Vte
from sugar3.graphics import style


class NavigationBar(Gtk.HBox):
    __gsignals__ = {
        'prev-clicked': (GObject.SignalFlags.RUN_LAST, None, ()),
        'next-clicked': (GObject.SignalFlags.RUN_LAST, None, ()),
        'replay-clicked': (GObject.SignalFlags.RUN_LAST, None, ()),
        'close-clicked': (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    
    def __init__(self):
        super(NavigationBar, self).__init__()
        self.set_homogeneous(False)
        self.set_spacing(style.DEFAULT_SPACING)
        
        # Previous button
        self._prev_button = Gtk.Button(_('← Previous'))
        self._prev_button.connect('clicked', self._prev_clicked_cb)
        self.pack_start(self._prev_button, False, False, 0)
        
        # Stage indicator (X / Total)
        self._stage_label = Gtk.Label()
        self._stage_label.set_margin_left(style.DEFAULT_PADDING)
        self._stage_label.set_margin_right(style.DEFAULT_PADDING)
        self.pack_start(self._stage_label, False, False, 0)
        
        # Next button
        self._next_button = Gtk.Button(_('Next →'))
        self._next_button.connect('clicked', self._next_clicked_cb)
        self.pack_start(self._next_button, False, False, 0)
        
        # Replay/Reload button
        self._replay_button = Gtk.Button(_('Replay'))
        self._replay_button.connect('clicked', self._replay_clicked_cb)
        self.pack_start(self._replay_button, False, False, 0)
        
        # Spacer
        spacer = Gtk.Label()
        self.pack_start(spacer, True, True, 0)
        
        # Close button
        self._close_button = Gtk.Button(_('Close'))
        self._close_button.connect('clicked', self._close_clicked_cb)
        self.pack_end(self._close_button, False, False, 0)
        
        self.show_all()
    
    def _prev_clicked_cb(self, button):
        self.emit('prev-clicked')
    
    def _next_clicked_cb(self, button):
        self.emit('next-clicked')
    
    def _replay_clicked_cb(self, button):
        self.emit('replay-clicked')
    
    def _close_clicked_cb(self, button):
        self.emit('close-clicked')
    
    def update_stage_info(self, current, total):
        """Update stage counter display."""
        self._stage_label.set_text(f"{current} / {total}")
        self._prev_button.set_sensitive(current > 1)
        self._next_button.set_sensitive(current < total)


class TutorialStage:
    def __init__(self, title, description, script_file=None, timing_file=None,
                 level="Beginner", objectives=None):
        self.title = title
        self.description = description
        self.script_file = script_file
        self.timing_file = timing_file
        self.level = level
        self.objectives = objectives or []
        self._replay_process = None
    
    def get_explanation_widget(self):
        vbox = Gtk.VBox(spacing=style.DEFAULT_PADDING)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup(f"<b><large>{self.title}</large></b>")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_line_wrap(True)
        vbox.pack_start(title_label, False, False, 0)
        
        # Level badge
        level_label = Gtk.Label(label=self.level)
        level_label.set_halign(Gtk.Align.START)
        level_context = level_label.get_style_context()
        if self.level == "Beginner":
            level_context.add_class("level-beginner")
        elif self.level == "Intermediate":
            level_context.add_class("level-intermediate")
        else:
            level_context.add_class("level-advanced")
        vbox.pack_start(level_label, False, False, 0)
        
        # Separator
        separator = Gtk.Separator()
        separator.set_orientation(Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(separator, False, False, 0)
        
        # Description
        desc_label = Gtk.Label(label=self.description)
        desc_label.set_line_wrap(True)
        desc_label.set_halign(Gtk.Align.START)
        desc_label.set_justify(Gtk.Justification.FILL)
        desc_label.set_margin_top(style.DEFAULT_PADDING)
        desc_label.set_margin_bottom(style.DEFAULT_PADDING)
        vbox.pack_start(desc_label, True, True, 0)
        
        # Objectives
        if self.objectives:
            obj_title = Gtk.Label()
            obj_title.set_markup("<b>Learning Objectives:</b>")
            obj_title.set_halign(Gtk.Align.START)
            vbox.pack_start(obj_title, False, False, 0)
            
            for obj in self.objectives:
                obj_label = Gtk.Label(label=f"• {obj}")
                obj_label.set_halign(Gtk.Align.START)
                obj_label.set_line_wrap(True)
                obj_label.set_margin_left(style.DEFAULT_PADDING)
                vbox.pack_start(obj_label, False, False, 0)
        
        vbox.set_margin_top(style.DEFAULT_PADDING)
        vbox.set_margin_left(style.DEFAULT_PADDING)
        vbox.set_margin_right(style.DEFAULT_PADDING)
        vbox.set_margin_bottom(style.DEFAULT_PADDING)
        
        return vbox
    
    def start_replay(self, vte_terminal):
        if not self.script_file or not self.timing_file:
            return False
        
        if not os.path.exists(self.script_file) or not os.path.exists(self.timing_file):
            return False
        
        # Clear terminal
        vte_terminal.feed_child(b"clear\n")
        
        try:
            import subprocess
            
            # Start scriptreplay process
            self._replay_process = subprocess.Popen(
                ['scriptreplay', '--maxdelay', '1.0',
                 self.timing_file, self.script_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return True
        except (OSError, FileNotFoundError):
            # scriptreplay not available; provide fallback
            vte_terminal.feed_child(
                b"# Script replay not available. Try 'man scriptreplay'\n"
            )
            return False
    
    def stop_replay(self):
        """Stop current script replay."""
        if self._replay_process:
            try:
                self._replay_process.terminate()
                self._replay_process.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                self._replay_process.kill()
            self._replay_process = None


class HelpTutorialWidget(Gtk.Box):
    
    def __init__(self, stages):
        super(HelpTutorialWidget, self).__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=style.DEFAULT_SPACING
        )
        
        self._stages = stages
        self._current_stage_idx = 0
        
        # Main content area with two columns
        content_box = Gtk.HBox(spacing=style.DEFAULT_SPACING)
        
        # Left: Explanation (scrollable)
        left_scroll = Gtk.ScrolledWindow()
        left_scroll.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )
        self._explanation_box = Gtk.VBox()
        left_scroll.add_with_viewport(self._explanation_box)
        
        # Right: Terminal
        self._vte_terminal = Vte.Terminal()
        self._vte_terminal.set_scrollback_lines(1000)
        
        # Split 50/50
        content_box.pack_start(left_scroll, True, True, 0)
        content_box.pack_start(self._vte_terminal, True, True, 0)
        
        # Navigation bar
        self._nav_bar = NavigationBar()
        self._nav_bar.connect('prev-clicked', self._prev_stage_cb)
        self._nav_bar.connect('next-clicked', self._next_stage_cb)
        self._nav_bar.connect('replay-clicked', self._replay_stage_cb)
        
        self.pack_start(content_box, True, True, 0)
        self.pack_end(self._nav_bar, False, False, 0)
        
        # Show first stage
        self._show_stage(0)
        self.show_all()
    
    def _show_stage(self, idx):
        """Display stage at given index."""
        if idx < 0 or idx >= len(self._stages):
            return
        
        self._current_stage_idx = idx
        stage = self._stages[idx]
        
        # Clear and update explanation
        for child in self._explanation_box.get_children():
            child.destroy()
        
        explanation_widget = stage.get_explanation_widget()
        self._explanation_box.pack_start(explanation_widget, True, True, 0)
        self._explanation_box.show_all()
        
        # Update navigation bar
        self._nav_bar.update_stage_info(idx + 1, len(self._stages))
        
        # Start terminal replay
        stage.start_replay(self._vte_terminal)
    
    def _prev_stage_cb(self, widget):
        self._stages[self._current_stage_idx].stop_replay()
        self._show_stage(self._current_stage_idx - 1)
    
    def _next_stage_cb(self, widget):
        self._stages[self._current_stage_idx].stop_replay()
        self._show_stage(self._current_stage_idx + 1)
    
    def _replay_stage_cb(self, widget):
        """Replay current stage."""
        stage = self._stages[self._current_stage_idx]
        stage.stop_replay()
        stage.start_replay(self._vte_terminal)
