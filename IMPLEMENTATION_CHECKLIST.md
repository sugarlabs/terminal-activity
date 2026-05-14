# Implementation Checklist

## Phase 1: Verification & Testing
- [ ] Run `python3 test_help_setup.py`
  - Verify all Python modules available
  - Check GTK3 and Vte installed
  - Confirm scriptreplay command present
- [ ] Run `python3 test_help_widget.py`
  - See widget in isolated window
  - Test navigation controls
  - Verify UI layout
- [ ] Review documentation
  - [ ] Read QUICKSTART.md
  - [ ] Read HELP_SYSTEM_DESIGN.md (sections 1-3)
  - [ ] Skim INTEGRATION_GUIDE.md

## Phase 2: Script Recording
- [ ] Record Stage 1: Recognizing the Prompt
  ```bash
  cd scripts/01_basics
  script --timing=01_prompt.timing 01_prompt.txt
  ```
- [ ] Record Stage 2: The Text Cursor
- [ ] Record Stage 3: Typing Commands & Echo
- [ ] Record Stage 4: REPL Basics
- [ ] Record Stage 5: Command Repeatability
- [ ] Record Stage 6: Python Interactive Mode
- [ ] Record remaining stages (7-20)
  - See tutorial_stages.py for descriptions
  - See scripts/README.md for tips

Progress: ____ / 20 stages recorded

## Phase 3: Integration Setup
- [ ] Read INTEGRATION_GUIDE.md completely
- [ ] Choose integration approach:
  - [ ] Option A: Replace existing help (recommended)
  - [ ] Option B: Add as separate feature
- [ ] Backup terminal.py
  ```bash
  cp terminal.py terminal.py.backup
  ```
- [ ] Add imports to terminal.py
  ```python
  from interactive_help import HelpTutorialWidget
  from tutorial_stages import TutorialStages
  ```

## Phase 4: Code Integration
- [ ] Add `_InteractiveHelpWindow` class to terminal.py
- [ ] Modify `_create_help_button()` method
- [ ] Add `_show_interactive_help_cb()` handler
- [ ] Connect help button to new handler
- [ ] Test imports: `python3 -c "from interactive_help import HelpTutorialWidget"`

## Phase 5: Testing in Activity
- [ ] Run Terminal Activity: `sugar-activity terminal.py`
- [ ] Click Help button
  - [ ] Window opens
  - [ ] All 20 stages accessible
  - [ ] Navigation works (prev/next)
  - [ ] Replay button works
  - [ ] Close button exits properly
  - [ ] Stage counter displays correctly
- [ ] Test with multiple scripts
  - [ ] Verify timing is appropriate
  - [ ] Check output is readable
  - [ ] Confirm no crashes

## Phase 6: Internationalization (i18n)
- [ ] Check po/POTFILES.in
  - [ ] Add interactive_help.py
  - [ ] Add tutorial_stages.py
- [ ] Extract strings: `xgettext ...`
- [ ] Update translation files

## Phase 7: Optimization & Polish
- [ ] Performance check
  - [ ] No memory leaks
  - [ ] Smooth navigation
  - [ ] Responsive UI
- [ ] Visual improvements
  - [ ] Icons for stage levels
  - [ ] Progress bar
  - [ ] Better styling
- [ ] Keyboard navigation
  - [ ] Arrow keys for prev/next
  - [ ] 'R' for replay
  - [ ] 'Esc' to close

## Phase 8: Final Testing
- [ ] Complete testing checklist from INTEGRATION_GUIDE.md
- [ ] Test on different screen sizes
- [ ] Test with long outputs
- [ ] Test script replay timing
- [ ] Verify no crashes or errors

## Optional: Future Enhancements
- [ ] Interactive mode (pause for user interaction)
- [ ] Quiz/validation after stages
- [ ] Asciinema support
- [ ] Video integration
- [ ] Mobile-responsive layout
- [ ] Custom terminal themes
- [ ] Stage bookmarks/favorites

## Key Files Reference

### Documentation (READ FIRST)
- QUICKSTART.md - 5-step overview
- IMPLEMENTATION_SUMMARY.md - What was created
- HELP_SYSTEM_DESIGN.md - Complete architecture
- INTEGRATION_GUIDE.md - How to integrate

### Code
- interactive_help.py - Widget implementation
- tutorial_stages.py - 20 tutorial definitions

### Testing
- test_help_setup.py - Verify environment
- test_help_widget.py - Test widget standalone

### Scripts
- scripts/README.md - Recording instructions
- scripts/01_basics/ through scripts/08_resources/ - Demo storage

## Troubleshooting During Implementation

### Problem: Import errors
**Solution:** 
1. Run `test_help_setup.py`
2. Ensure files are in correct directory
3. Check Python version (need 3.6+)

### Problem: Vte not available
**Solution:**
```bash
# Install GObject introspection bindings
sudo apt install gir1.2-vte-2.91  # Debian
sudo dnf install vte291-devel     # Fedora
```

### Problem: scriptreplay not found
**Solution:**
```bash
sudo apt install util-linux  # Debian
sudo dnf install util-linux  # Fedora
```

### Problem: Widget doesn't display
**Solution:**
1. Test with `test_help_widget.py` first
2. Check terminal output for errors
3. Verify Gtk/Vte imports work

### Problem: Scripts don't replay
**Solution:**
1. Verify script files exist
2. Test replay manually: `scriptreplay --maxdelay 1.0 timing.txt script.txt`
3. Check file paths in tutorial_stages.py

## Progress Tracking

### Documentation & Code
- [x] interactive_help.py created
- [x] tutorial_stages.py created
- [x] HELP_SYSTEM_DESIGN.md created
- [x] INTEGRATION_GUIDE.md created
- [x] scripts/README.md created
- [x] QUICKSTART.md created
- [x] IMPLEMENTATION_SUMMARY.md created
- [x] test_help_setup.py created
- [x] test_help_widget.py created
- [x] Directory structure created

### Next: Recording Scripts
- [ ] Record all 20 demo scripts
- [ ] Test replay for each
- [ ] Verify timing is good

### Integration
- [ ] Integrate into terminal.py
- [ ] Test with Terminal Activity
- [ ] Complete full testing

### Completion
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Ready for release

## Estimated Timeline

**Phase 1-2:** 1-2 hours (verification + basic recording)
**Phase 3-4:** 1-2 hours (integration setup & code)
**Phase 5-6:** 2-3 hours (activity testing & i18n)
**Phase 7-8:** 1-2 hours (optimization & final testing)

**Total:** 6-10 hours for full implementation

## Success Criteria

✓ Help widget opens in isolated window
✓ All 20 tutorial stages accessible
✓ Navigation works (prev/next/replay/close)
✓ Stage explanations display correctly
✓ VTE terminal shows script replays
✓ Integrated into Terminal Activity
✓ Help button launches help window
✓ No crashes or memory leaks
✓ i18n strings extracted
✓ Full documentation present

For detailed instructions on each phase, see the corresponding document:
- Phase 1-2: QUICKSTART.md
- Phase 3-4: INTEGRATION_GUIDE.md  
- Phase 5: INTEGRATION_GUIDE.md (i18n section)
- Phase 6-8: INTEGRATION_GUIDE.md (testing checklist)

