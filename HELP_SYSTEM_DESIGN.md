# Terminal Activity: Interactive Scripted Help System
## Overview
Enhancement to Terminal Activity help system, extending from the current palette-based static help (added 2012 by @godiard and @aguzubiaga) into an interactive, scripted terminal tutorial system using Vte (Virtual Terminal Emulator) and timing-based demonstrations.

**Inspiration**: Implode Activity's multi-stage embedded help pattern with animations and navigation.

---

## Current State
### Existing Help System
- **HelpButton** (helpbutton.py): Gtk.ToolItem with popup palette
- **Content**: Static text about basic commands (cd, ls, cp, rm, su)
- **Limitations**: No interactivity, no live demonstrations, no progression

### Reference Implementation
- **Implode Activity** (GitHub: sugarlabs/implode-activity)
  - Gtk.Notebook-based multi-stage tutorial
  - Modal dialog window with navigation (Previous/Next/Replay)
  - Gtk.DrawingArea for animated demonstrations
  - Well-structured stage classes

## Design: Interactive Terminal Help System

### Core Components

#### 1. **TutorialStage** (Base Class)
Each tutorial stage includes:
- **Title**: Topic name (e.g., "Recognizing the Prompt")
- **Description**: Learning objectives and explanatory text
- **Script data**: Timing information and commands to replay
- **Level**: Beginner/Intermediate/Advanced
- **Topics**: Category tags

```python
class TutorialStage:
    """Base class for tutorial stages"""
    def __init__(self, title, description, script_file, level="Beginner"):
        self.title = title
        self.description = description
        self.script_file = script_file  # Recorded script(1) output
        self.timing_file = timing_file  # Timing data
        self.level = level
        self.objectives = []
    
    def get_explanation_widget(self):
        """Return Gtk widget with explanation"""
        pass
    
    def start_replay(self, vte_terminal):
        """Start scriptreplay(1) on terminal"""
        pass
    
    def stop_replay(self):
        """Stop current replay"""
        pass
```

#### 2. **HelpTutorialWidget** (Main Tutorial Container)
Manages stage progression and UI layout:

```python
class HelpTutorialWidget(Gtk.Box):
    def __init__(self):
        self._stages = [
            # Basics
            TutorialStage("Recognizing the Prompt", ...),
            TutorialStage("The Text Cursor", ...),
            TutorialStage("Command Echo", ...),
            # Fundamentals
            TutorialStage("REPL Basics", ...),
            TutorialStage("Command Repeatability", ...),
            # Error Handling
            TutorialStage("Mistakes & Recovery", ...),
            # Advanced
            TutorialStage("Long Output & Scrolling", ...),
            TutorialStage("Typical Tasks", ...),
            # System Level
            TutorialStage("System Investigation", ...),
            TutorialStage("Package Management", ...),
            # Resources
            TutorialStage("Finding Help", ...),
        ]
        self._current_stage = 0
        self._notebook = Gtk.Notebook()
        self._setup_ui()
    
    def next_stage(self):
        """Move to next tutorial stage"""
        self._stop_current_replay()
        self._current_stage = min(self._current_stage + 1, len(self._stages) - 1)
        self._show_stage(self._current_stage)
    
    def prev_stage(self):
        """Move to previous tutorial stage"""
        self._stop_current_replay()
        self._current_stage = max(self._current_stage - 1, 0)
        self._show_stage(self._current_stage)
    
    def replay(self):
        """Restart current stage's terminal replay"""
        self._stop_current_replay()
        self._stages[self._current_stage].start_replay(self._vte)
```

#### 3. **Script Replay System** Using script(1) & scriptreplay(1)

**Recording process** (one-time, during activity development):
```bash
script --timing=timing_file.txt script_file.txt
# Type commands interactively...
# Press Ctrl+D to finish
```

**Replay process** (in HelpTutorialWidget):
```python
def start_replay(self, vte_terminal):
    # Clear terminal
    vte_terminal.feed_child("clear\n".encode())
    
    # Start scriptreplay(1) process
    import subprocess
    self._replay_proc = subprocess.Popen([
        'scriptreplay',
        '--maxdelay', '1.0',  # Cap delay between commands
        self.timing_file,
        self.script_file
    ], stdout=vte_terminal.get_fd(), stderr=subprocess.PIPE)
```

**Alternative (Modern)**: asciinema format
- Can use `asciinema` recordings for more polished demonstrations
- Provides better control over timing and replay

## Tutorial Stages & Topics
### Stage Hierarchy

#### **Level 1: Basics** (New to terminal)
1. **Recognizing the Prompt**
   - What is a command prompt?
   - Prompt components ($, #, user@host)
   - Text cursor blinking
   
2. **Typing & Echoing**
   - Command echo as you type
   - Example: `df -h .`
   - Output format recognition

3. **Understanding Output**
   - Reading directory listings
   - File permissions, sizes, dates
   - Return to prompt

#### **Level 2: Fundamentals** (REPL Concepts)
4. **REPL Basics**
   - Read-Eval-Print-Loop explained
   - Waits for input forever
   - Executes exactly what you ask
   - Interactive demonstration with Python

5. **Command Repeatability**
   - Every command is repeatable
   - Same input = same output
   - History and re-execution

#### **Level 3: Error Handling**
6. **Making Mistakes**
   - Common errors (command not found, permission denied)
   - Shell command recall (↑ history)
   - Editing commands (← → keys, Ctrl+A/E)
   - Safe deletion practices

7. **Accidental Destruction Prevention**
   - Understanding `rm` dangers
   - Using `rm -i` for interactive mode
   - Trash/backup alternatives

#### **Level 4: Advanced Terminal Skills**
8. **Copying & Pasting**
   - Selecting text with mouse
   - Clipboard operations
   - Pasting into terminal

9. **Handling Long Output**
   - `ls -laR` for deep directory traversal
   - Scrolling through output (mouse wheel, Page Up/Down)
   - Returning to prompt after viewing

10. **Piping & Output Redirection**
    - Understanding pipes (`|`)
    - Output redirection (`>`, `>>`)
    - Combining commands

#### **Level 5: User-Level Tasks**
11. **Filesystem Tools**
    - `cd`, `ls`, `cp`, `mv`, `mkdir`, `rm`, `touch`
    - Path navigation (relative vs absolute)
    - Wildcards and globbing

12. **Starting Graphical Programs**
    - Running GUI apps from terminal (`gedit`, `firefox &`)
    - Background processes (&)
    - Process management

13. **Python REPL**
    - Entering Python interactive mode
    - Basic Python commands
    - Exiting REPL (Ctrl+D or exit())

#### **Level 6: Sugar-Specific Tasks**
14. **Sugar Settings (gsettings)**
    - Querying Sugar configuration
    - Changing settings safely
    - Listing available keys

15. **Cloning an Activity**
    - Cloning from Git
    - Directory structure
    - Running activities

#### **Level 7: System-Level Tasks**
16. **Investigating Your System**
    - `uname`, `lsb_release`, `cat /etc/os-release`
    - Detecting Fedora vs Debian
    - System information queries

17. **Package Management**
    - Fedora: `dnf search`, `dnf install` (with sudo)
    - Debian: `apt search`, `apt install` (with sudo)
    - Context-aware demonstrations

18. **Software Installation**
    - Installing Python packages: `pip install`
    - Using virtual environments
    - Safety considerations

#### **Level 8: Resources & Getting Help**
19. **Finding Commands**
    - `man command` for manual pages
    - `command --help` for quick help
    - Searching for functionality

20. **Online Documentation**
    - Sugar Labs documentation
    - Linux man pages online
    - Stack Overflow & community resources

---

## Implementation Plan
### Phase 1: Core Infrastructure
- [ ] Create `interactive_help.py` module with base classes
  - `TutorialStage` base class
  - `HelpTutorialWidget` container
  - `NavigationBar` widget
  
- [ ] Create `script_replay.py` for script(1)/scriptreplay(1) integration
  - Subprocess management
  - Terminal feed handling
  - Timing synchronization

- [ ] Create `tutorial_stages.py` with stage definitions
  - Import `TutorialStage`
  - Define all 20 tutorial stages
  - Associate script files

### Phase 2: Script Recordings
- [ ] Create `scripts/` directory for recorded demonstrations
  - Subdirectories by level/topic
  - Format: `script_file.txt` and `timing_file.txt` pairs
  
- [ ] Record demonstrations using `script(1)` for each stage
  - Clean, well-paced demonstrations
  - Clear explanatory narration via comments in scripts
  - Consistent timing (maxdelay capped at 1.0s)

- [ ] Create `scripts/README.md` documenting recording process

### Phase 3: Integration with Terminal Activity
- [ ] Modify `terminal.py` help button click handler
  - Replace simple palette with HelpTutorialWidget
  - Launch modal HelpWindow
  
- [ ] Update `helpbutton.py` or create new `help_window.py`
  - Modal window with close button
  - Proper sizing and positioning

### Phase 4: UI/UX Polish
- [ ] Add visual indicators
  - Current stage number (X/Y)
  - Progress bar showing tutorial progression
  - Level indicators (Beginner/Intermediate/Advanced)

- [ ] Add keyboard navigation
  - Left/Right arrows for Previous/Next
  - R for Replay
  - Esc to close

- [ ] Internationalization (i18n)
  - Extract strings using xgettext
  - Support translation of stage descriptions

### Phase 5: Testing & Refinement
- [ ] Test all script replays
- [ ] Verify timing synchronization
- [ ] Test on different terminal sizes
- [ ] Verify Vte integration on target platform
- [ ] Performance testing (memory, CPU during replay)

## Technical Considerations
### Dependencies
- **Existing**: Sugar3, Gtk3, Vte (VteTerminal)
- **New**: Python subprocess module (standard library)
- **Optional**: asciinema package for modern alternative

### Vte Terminal Integration
```python
from gi.repository import Vte

class HelpTerminalBox(Gtk.Box):
    def __init__(self):
        self._terminal = Vte.Terminal()
        self._terminal.connect("child-exited", self._child_exited_cb)
        self.pack_start(self._terminal, True, True, 0)
    
    def get_fd(self):
        """Get file descriptor for scriptreplay output"""
        return self._terminal.get_pty().get_fd()
```

### Script File Format
- **Script file**: Plain text, output of `script(1)` command
- **Timing file**: Two columns: seconds elapsed, bytes output
- **Alternative**: JSON-based timing for better control

### Cross-Platform Concerns
- Fedora vs Debian detection for package manager examples
- File paths (Windows vs Linux)
- Terminal size assumptions

## Files to Create/Modify

### New Files
- `interactive_help.py` - Core widget classes
- `script_replay.py` - Script/timing playback engine
- `tutorial_stages.py` - Stage definitions
- `scripts/` - Directory with recorded demonstrations
- `scripts/README.md` - Recording documentation
- `HELP_SYSTEM_DESIGN.md` - This design document

### Modified Files
- `terminal.py` - Help button integration
- `helpbutton.py` - Or replace with new help_window.py
- `setup.py` - Add any new dependencies
- `po/` - i18n strings for new help content

## Future Enhancements

1. **Interactive Mode**: Commands that pause for user interaction
2. **Quiz/Validation**: Check user understanding after stages
3. **Custom Paths**: Users can record custom tutorials
4. **Video Integration**: Embed asciinema directly
5. **Accessibility**: Screen reader support for tutorials
6. **Mobile-Friendly**: Responsive layout for different screen sizes
7. **Offline Content**: Bundle scripts with activity for offline use
8. **Analytics**: Track which stages users visit most

## Resources

- Sugar Labs: https://sugarlabs.org/
- Terminal Activity: https://github.com/sugarlabs/terminal-activity
- Implode Activity: https://github.com/sugarlabs/implode-activity
- script(1) man page: https://linux.die.net/man/1/script
- scriptreplay(1) man page: https://linux.die.net/man/1/scriptreplay
- Vte (GTK Bindings): https://lazka.github.io/pgi-docs/
- asciinema: https://asciinema.org/
