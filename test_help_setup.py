import sys
import os
def test_imports():
    print("=" * 60)
    print("Testing Interactive Help System Setup")
    print("=" * 60)
    print()
    
    # Test standard library imports
    print("1. Testing standard library imports...")
    try:
        import subprocess
        import gi
        print("   subprocess, gi modules OK")
    except ImportError as e:
        print(f"   Error: {e}")
        return False
    
    # Test GTK/Vte imports
    print("2. Testing GTK3 and Vte imports...")
    try:
        gi.require_version('Gtk', '3.0')
        gi.require_version('Vte', '2.91')
        from gi.repository import Gtk, Gdk, GObject, Vte
        print("   Gtk 3.0, Vte 2.91+ available")
    except (ImportError, ValueError) as e:
        print(f"   Error: {e}")
        print("   Install with: sudo apt install python3-gi gir1.2-vte-2.91")
        return False
    
    # Test Sugar3 imports
    print("3. Testing Sugar3 imports...")
    try:
        from sugar3.graphics import style
        print("   sugar3.graphics available")
    except ImportError as e:
        print(f"   Warning: {e}")
        print("   (This is OK if not running in Sugar environment)")
    
    # Test project-specific modules
    print("4. Testing interactive help module...")
    try:
        from interactive_help import TutorialStage, HelpTutorialWidget, NavigationBar
        print("   interactive_help.py imports successfully")
    except ImportError as e:
        print(f"   Error: {e}")
        return False
    
    print("5. Testing tutorial stages module...")
    try:
        from tutorial_stages import TutorialStages
        print("   tutorial_stages.py imports successfully")
    except ImportError as e:
        print(f"   Error: {e}")
        return False
    
    return True


def test_stages():
    print()
    print("6. Loading tutorial stages...")
    try:
        from tutorial_stages import TutorialStages
        stages = TutorialStages.get_all_stages()
        print(f"    Loaded {len(stages)} tutorial stages")
        
        # List by category
        print()
        print("   Tutorial Structure:")
        for i, stage in enumerate(stages, 1):
            level = stage.level
            objectives = len(stage.objectives)
            script_status = "✓" if stage.script_file else "○"
            print(f"      {i:2d}. [{script_status}] {stage.title}")
            print(f"          Level: {level}, Objectives: {objectives}")
        
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False


def test_script_files():
    print()
    print("7. Checking script files...")
    
    script_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    
    if not os.path.exists(script_dir):
        print(f"    Scripts directory not found: {script_dir}")
        print("     Create with: mkdir -p scripts/{{01_basics,02_fundamentals,...}}")
        return False
    
    # Count script files
    script_count = 0
    timing_count = 0
    
    for root, dirs, files in os.walk(script_dir):
        for f in files:
            if f.endswith('.txt'):
                script_count += 1
            elif f.endswith('.timing'):
                timing_count += 1
    
    if script_count == 0 and timing_count == 0:
        print(f"    No script files recorded yet in: {script_dir}")
        print("     See scripts/README.md for recording instructions")
    else:
        print(f"    Found {script_count} script files and {timing_count} timing files")
    
    return True


def test_commands():
    print()
    print("8. Checking scriptreplay command...")
    
    try:
        import subprocess
        result = subprocess.run(['which', 'scriptreplay'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"   scriptreplay found at: {result.stdout.strip()}")
        else:
            print("   scriptreplay command not found")
            print("     Install with:")
            print("       Fedora: sudo dnf install util-linux")
            print("       Debian: sudo apt install util-linux bsdutils")
            return False
    except Exception as e:
        print(f"   Error checking command: {e}")
        return False
    
    return True


def show_next_steps():
    print()
    print("=" * 60)
    print("Next Steps")
    print("=" * 60)
    print()
    print("1. Record Tutorial Scripts")
    print("   See: scripts/README.md for detailed recording instructions")
    print()
    print("   Quick start:")
    print("   $ cd scripts/01_basics")
    print("   $ script --timing=01_prompt.timing 01_prompt.txt")
    print("   [Type demonstration commands]")
    print("   [Ctrl+D to end]")
    print()
    print("2. Integrate with Terminal Activity")
    print("   See: INTEGRATION_GUIDE.md for step-by-step instructions")
    print()
    print("3. Test the Help Widget")
    print("   Run: python3 test_help_widget.py")
    print()
    print("4. Review Documentation")
    print("   - HELP_SYSTEM_DESIGN.md (architecture overview)")
    print("   - INTEGRATION_GUIDE.md (integration steps)")
    print("   - scripts/README.md (recording instructions)")
    print()


def main():
    # Test imports
    if not test_imports():
        print()
        print("Import test failed. Please install dependencies.")
        sys.exit(1)
    
    # Test stages
    if not test_stages():
        print()
        print("Tutorial stages test failed.")
        sys.exit(1)

    test_script_files()

    test_commands()

    show_next_steps()
    
    print("=" * 60)
    print("Setup test complete!")
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()
