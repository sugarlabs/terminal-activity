# Integration Guide: Interactive Help System

## Overview

This guide explains how to integrate the new interactive help system into Terminal Activity, replacing (or supplementing) the existing palette-based help button.

## Current Implementation

The current help system uses:
- **helpbutton.py**: `HelpButton` class providing a popup palette
- **terminal.py**: `_create_help_button()` method in the `TerminalActivity` class

Current structure in `terminal.py`:
```python
class TerminalActivity(activity.Activity):
    def __init__(self, handle):
        # ...
        self._create_help_button()
    
    def _create_help_button(self):
        helpitem = HelpButton()
        helpitem.add_section(_('Useful commands'))
        # ... add static help content ...
        return helpitem
```

## New Implementation

The new system provides:
- **interactive_help.py**: 
  - `TutorialStage` - Individual tutorial topics
  - `HelpTutorialWidget` - Main tutorial container with split layout
  - `NavigationBar` - Forward/back/replay controls

- **tutorial_stages.py**:
  - `TutorialStages` class - Collection of all 20 tutorial stages
  - Each stage maps to script files for demonstrations

- **scripts/**: Directory containing recorded demonstrations

## Integration Approach
### Option A: Replace Existing Help (Recommended)

Replace the palette-based help with a modal window containing the interactive tutorials.

#### Step 1: Modify terminal.py

Import the new modules at the top:

```python
# Add these imports to terminal.py
from interactive_help import HelpTutorialWidget, NavigationBar
from tutorial_stages import TutorialStages
```

#### Step 2: Create Help Window Class

Add a new help window class to terminal.py:

```python
class _InteractiveHelpWindow(Gtk.Window):
    """Modal dialog for interactive help tutorials."""
    
    def __init__(self, parent_activity):
        super(_InteractiveHelpWindow, self).__init__(
            type=Gtk.WindowType.TOPLEVEL
        )
        
        self.set_transient_for(parent_activity)
        self.set_modal(True)
        self.set_default_size(
            Gdk.Screen.width() - 100,
            Gdk.Screen.height() - 100
        )
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        
        # Get all tutorial stages
        stages = TutorialStages.get_all_stages()
        
        # Create help tutorial widget
        help_widget = HelpTutorialWidget(stages)
        
        # Connect close signal
        help_widget.connect('close-clicked', self._close_cb)
        
        self.add(help_widget)
        self.connect('delete-event', self._delete_event_cb)
        
        self.show_all()
    
    def _close_cb(self, widget):
        self.destroy()
    
    def _delete_event_cb(self, widget, event):
        self.destroy()
        return False
```

#### Step 3: Modify _create_help_button()

Replace the static help button creation with dynamic help window launching:

```python
def _create_help_button(self):
    """Create help button that launches interactive tutorial."""
    
    # Create a simple toolbar button
    help_button = ToolButton('toolbar-help')
    help_button.set_tooltip(_('Interactive Help'))
    help_button.connect('clicked', self._show_interactive_help_cb)
    
    return help_button

def _show_interactive_help_cb(self, button):
    """Launch interactive help window."""
    help_window = _InteractiveHelpWindow(self)
```

#### Step 4: Handle Navigation Bar Signals

The `NavigationBar` emits signals. Update the `HelpTutorialWidget` to handle the 'close-clicked' signal (already done in interactive_help.py).

### Option B: Add Interactive Help as Separate Feature

Keep the existing palette-based help and add interactive tutorials via a separate button or menu item.

#### Step 1: Create separate help menu item

```python
def _create_interactive_help_button(self):
    """Create interactive help button (separate from static help)."""
    
    help_button = ToolButton('toolbar-help')
    help_button.set_tooltip(_('Interactive Tutorial'))
    help_button.connect('clicked', self._show_interactive_help_cb)
    
    return help_button

def _show_interactive_help_cb(self, button):
    """Launch interactive help window."""
    help_window = _InteractiveHelpWindow(self)
```

Then add both buttons to toolbar in the activity initialization.

## Implementation Steps

### Step 1: Prepare Environment

```bash
# In terminal-activity directory
# Ensure all files are in place
ls -la interactive_help.py tutorial_stages.py scripts/
```

### Step 2: Test Imports

Create a test script to verify imports work:

```python
# test_help_import.py
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Vte

from interactive_help import HelpTutorialWidget, NavigationBar
from tutorial_stages import TutorialStages

# Get stages
stages = TutorialStages.get_all_stages()
print(f"Loaded {len(stages)} tutorial stages")
for i, stage in enumerate(stages, 1):
    print(f"  {i}. {stage.title}")

print("✓ Imports successful!")
```

Run: `python3 test_help_import.py`

### Step 3: Create Sample Recording

Create at least one sample script for testing:

```bash
cd scripts/01_basics

# Record first tutorial
script --timing=01_prompt.timing 01_prompt.txt

# In the script session:
clear
whoami
pwd
ls -la

# Ctrl+D to end
```

### Step 4: Test Help Widget in Isolation

```python
# test_help_widget.py
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk

from interactive_help import HelpTutorialWidget
from tutorial_stages import TutorialStages

# Create test window
win = Gtk.Window(Gtk.WindowType.TOPLEVEL)
win.set_default_size(1200, 700)
win.connect('destroy', Gtk.main_quit)

# Create help widget
stages = TutorialStages.get_all_stages()
help_widget = HelpTutorialWidget(stages)

win.add(help_widget)
win.show_all()

Gtk.main()
```

### Step 5: Integrate into terminal.py

Follow Option A or Option B above to integrate the help window.

### Step 6: Test in Activity

```bash
# Run Terminal Activity
sugar-activity terminal.py
```

Click the Help button to verify:
- ✓ Window opens correctly
- ✓ Tutorial stages display
- ✓ Navigation works (prev/next/replay)
- ✓ Explanation text is readable
- ✓ VTE terminal displays (even if scripts don't exist)

### Step 7: Internationalization (i18n)

Extract translatable strings:

```bash
# Generate POT file
xgettext -f po/POTFILES.in -o po/terminal.pot

# The _() function calls in interactive_help.py and tutorial_stages.py 
# will be automatically extracted
```

## File Modifications Checklist

- [ ] Add imports to `terminal.py`
- [ ] Add `_InteractiveHelpWindow` class to `terminal.py`
- [ ] Modify `_create_help_button()` in `terminal.py` (or add new method)
- [ ] Connect help button click to help window launch
- [ ] Test imports and basic widget
- [ ] Record at least 2-3 sample scripts
- [ ] Update `setup.py` if new dependencies added
- [ ] Test full integration in Terminal Activity
- [ ] Run `sugar-activity` to verify

## Dependencies

### Required
- Python 3.x
- PyGObject (gi) with Gtk 3.0 and Vte 2.91+
- script/scriptreplay commands (standard on Linux)

### Already in Terminal Activity
- sugar3 package
- gi.repository.Gtk

### Verify availability

```bash
# Test Vte availability
python3 -c "from gi.repository import Vte; print('Vte OK')"

# Test scriptreplay
which scriptreplay
```

## Troubleshooting Integration

### Problem: "No module named 'interactive_help'"
**Solution**: Ensure `interactive_help.py` is in the same directory as `terminal.py`

### Problem: Vte import fails
**Solution**: Install gobject-introspection bindings:
- Fedora: `sudo dnf install python3-gi`
- Debian: `sudo apt install python3-gi`

### Problem: Window doesn't appear
**Solution**: 
- Check if Gtk initialization is correct
- Verify `set_transient_for()` and `set_modal()` calls
- Test with standalone script first

### Problem: Scripts don't replay
**Solution**:
- Verify script files exist in correct directory
- Test scriptreplay manually: `scriptreplay --maxdelay 1.0 timing_file.txt script_file.txt`
- Add debug logging to `TutorialStage.start_replay()` method

### Problem: i18n strings not extracted
**Solution**:
- Ensure po/POTFILES.in lists `interactive_help.py` and `tutorial_stages.py`
- Re-run xgettext extraction
- Check that _() function is properly imported from gettext

## Testing Checklist

- [ ] Help button launches help window
- [ ] All 20 tutorial stages are accessible
- [ ] Can navigate forward and backward through stages
- [ ] Replay button works (or gracefully handles missing scripts)
- [ ] Close button properly closes window
- [ ] Navigation bar updates correctly (prev/next enable/disable)
- [ ] Stage number counter updates
- [ ] Explanation text is readable and formatted well
- [ ] VTE terminal displays and is focused
- [ ] No memory leaks when opening/closing help multiple times
- [ ] Activity continues running while help is open
- [ ] Help window closes properly without crashing activity

## Next Steps After Integration

1. **Record all 20 tutorial scripts** - Start with basics, expand to advanced
2. **i18n translations** - Add to translation workflow
3. **Visual enhancements** - Add icons, colors, progress bar
4. **Keyboard shortcuts** - Add Alt+H or similar for help
5. **Context-sensitive help** - Show relevant stage based on activity state
6. **User feedback** - Collect which stages are most useful
7. **Script improvements** - Refine timing, add more examples
8. **Mobile/Tablet support** - Adjust layout for smaller screens

## References

- [HELP_SYSTEM_DESIGN.md](HELP_SYSTEM_DESIGN.md) - Architecture overview
- [scripts/README.md](scripts/README.md) - Recording instructions
- [interactive_help.py](interactive_help.py) - Widget implementation
- [tutorial_stages.py](tutorial_stages.py) - Stage definitions
- Terminal Activity: https://github.com/sugarlabs/terminal-activity
- Implode Activity (reference): https://github.com/sugarlabs/implode-activity

