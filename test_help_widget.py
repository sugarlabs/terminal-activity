import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')

from gi.repository import Gtk, Gdk

try:
    from sugar3.graphics import style
except ImportError:
    class MockStyle:
        DEFAULT_SPACING = 10
        DEFAULT_PADDING = 10
        GRID_CELL_SIZE = 50
    
    # Create mock module
    sys.modules['sugar3'] = type(sys)('sugar3')
    sys.modules['sugar3.graphics'] = type(sys)('sugar3.graphics')
    sys.modules['sugar3.graphics.style'] = MockStyle()

from interactive_help import HelpTutorialWidget
from tutorial_stages import TutorialStages


def create_main_window():
    
    window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
    window.set_title("Interactive Help System - Test Widget")
    window.set_default_size(1200, 700)
    window.connect("destroy", Gtk.main_quit)
    
    # Get tutorial stages
    print("Loading tutorial stages...")
    stages = TutorialStages.get_all_stages()
    print(f"Loaded {len(stages)} stages:")
    for i, stage in enumerate(stages, 1):
        print(f"  {i}. {stage.title}")
    
    print("\nCreating help tutorial widget...")
    try:
        help_widget = HelpTutorialWidget(stages)
        print(" Help widget created successfully")
    except Exception as e:
        print(f" Error creating help widget: {e}")
        import traceback
        traceback.print_exc()
        return None

    window.add(help_widget)

    window.show_all()
    
    print("\n" + "=" * 60)
    print("Help Tutorial Widget Test Window")
    print("=" * 60)
    print("\nWindow is open. Test the following:")
    print("  • Explanation text renders correctly")
    print("  • VTE terminal is visible on the right")
    print("  • Navigation bar shows at the bottom")
    print("  • Use buttons to navigate between stages")
    print("  • Check stage counter (X / 20)")
    print("  • Verify replay button works")
    print("\nClose the window to exit.")
    print()
    
    return window


def show_usage():
    print("""
Interactive Help Widget Test Script

This script tests the help tutorial widget in isolation.

Prerequisites:
  - Python 3.x
  - PyGObject (gi) with Gtk 3.0 and Vte 2.91+
  - script/scriptreplay commands (for actual replay)

Features tested:
  - Tutorial stage loading
  - Widget initialization
  - Navigation controls
  - UI layout (split pane with explanation and terminal)

Usage:
  python3 test_help_widget.py

Troubleshooting:

1. "ImportError: No module named 'gi'"
   Install: sudo apt install python3-gi

2. "ImportError: No module named 'sugar3'"
   This script includes a mock sugar3 for testing.
   If outside Sugar environment, mocks are created.

3. VTE terminal shows error
   This is expected if no script files exist yet.
   See scripts/README.md for recording instructions.

4. UI rendering issues
   Check GTK version: python3 -c "from gi.repository import Gtk; print(Gtk.MAJOR_VERSION)"
   Should be version 3.x

Controls:
  - Use Previous/Next buttons to navigate stages
  - Click Replay to restart current stage demo
  - Click Close to exit

Notes:
  - Stage numbering starts at 1
  - Scripts are optional; widget works without them
  - Navigation is keyboard accessible (Tab, Space, Enter)
""")


def main():
    
    print("\n" + "=" * 60)
    print("Testing Interactive Help Widget")
    print("=" * 60)
    print()

    show_usage()

    print("Checking requirements...")
    
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        gi.require_version('Vte', '2.91')
        from gi.repository import Gtk, Gdk, Vte
        print(" GTK 3.0 and Vte 2.91+ available")
    except (ImportError, ValueError) as e:
        print(f" Missing requirement: {e}")
        print("Install with: sudo apt install python3-gi gir1.2-vte-2.91")
        sys.exit(1)
    
    try:
        from interactive_help import HelpTutorialWidget
        from tutorial_stages import TutorialStages
        print(" Help modules can be imported")
    except ImportError as e:
        print(f" Cannot import help modules: {e}")
        sys.exit(1)
 
    print()
    window = create_main_window()
    
    if window:
        try:
            Gtk.main()
        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            sys.exit(0)
    else:
        print(" Failed to create test window.")
        sys.exit(1)


if __name__ == '__main__':
    main()
