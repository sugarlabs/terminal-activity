# Terminal Activity Tutorial Scripts

This directory contains recorded terminal demonstrations for the interactive help system.

## Recording Format

Each tutorial uses two files:
- `NN_description.txt` - Raw script output from `script(1)` command
- `NN_description.timing` - Timing data from `script(1)` command

These are replayed during help sessions using `scriptreplay(1)`.

---

## Recording a Tutorial Script

### Prerequisites
Ensure you have the `script` and `scriptreplay` commands available (standard on Linux):

```bash
which script scriptreplay
```

If not available, install:
- **Fedora**: `sudo dnf install util-linux`
- **Debian/Ubuntu**: `sudo apt install bsdutils` or `sudo apt install util-linux`

### Step-by-Step Recording

1. **Create a clean environment** for recording:
   ```bash
   # Optional: Start in a temp directory to keep demo files contained
   mkdir -p ~/demo-terminal
   cd ~/demo-terminal
   ```

2. **Start recording with timing**:
   ```bash
   script --timing=timing_file.txt script_file.txt
   ```
   
   This displays:
   ```
   Script started, file is script_file.txt
   ```

3. **Clear the terminal** to start fresh:
   ```bash
   clear
   ```

4. **Type your demonstration commands**:
   - Speak out loud or type comments explaining what you're doing
   - Use natural pace; scriptreplay can cap delays later
   - Include typical mistakes and corrections where relevant
   - End with a clear return to the prompt

5. **Example demonstration** (for "Recognizing the Prompt" stage):
   ```bash
   # This is a demo script
   # Let me show you the command prompt
   pwd
   ls -la
   whoami
   ```

6. **Exit the recording**:
   - Press `Ctrl+D` or type `exit` and Enter

   You'll see:
   ```
   Script done, file is script_file.txt
   ```

7. **Verify the files were created**:
   ```bash
   ls -lah script_file.txt timing_file.txt
   ```

---

## File Organization

Scripts are organized by level and topic:

```
scripts/
├── 01_basics/
│   ├── 01_prompt.txt
│   ├── 01_prompt.timing
│   ├── 02_cursor.txt
│   ├── 02_cursor.timing
│   ├── 03_echo.txt
│   └── 03_echo.timing
├── 02_fundamentals/
│   ├── 04_repl.txt
│   ├── 04_repl.timing
│   ├── 05_repeatability.txt
│   ├── 05_repeatability.timing
│   ├── 06_python_repl.txt
│   └── 06_python_repl.timing
├── 03_errors/
├── 04_advanced/
├── 05_user_tasks/
├── 06_sugar_tasks/
├── 07_system_tasks/
└── 08_resources/
```

**File naming convention**: `NN_topic_name.txt` and `NN_topic_name.timing`
- `NN` = two-digit stage number (01-20)
- `topic_name` = descriptive name

---

## Testing Your Recording

After creating script and timing files, test them locally:

```bash
# Test with scriptreplay
scriptreplay --maxdelay 1.0 timing_file.txt script_file.txt

# Or with asciinema (if available)
asciinema play timing_file.txt
```

Verify:
- ✓ Output displays correctly
- ✓ Timing is reasonable (not too fast, not too slow)
- ✓ All content is visible before the session ends
- ✓ Returns to prompt clearly

---

## Recording Tips & Best Practices

### Pacing
- Natural typing speed (~40-60 WPM) is usually good
- Brief pauses (1-2 seconds) let viewers read output
- Longer pauses (3+ seconds) can be capped with `scriptreplay --maxdelay 1.0`

### Content
- Start with `clear` for a clean beginning
- Use `echo` to add explanatory comments:
  ```bash
  echo "=== Listing files in current directory ==="
  ls -la
  ```
- Include realistic mistakes and corrections to show error handling
- End clearly at the prompt

### Recording Environment
- Use a standard terminal (bash/sh)
- Set terminal size appropriately:
  ```bash
  stty rows 24 cols 80
  ```
- Avoid terminal-specific features or coloring that won't display in scriptreplay

### File Sizes
- Keep individual scripts reasonable (~100-500 lines)
- Multiple shorter scripts are better than one long script
- Consider splitting complex topics into sub-topics

### Avoiding Issues

**Problem**: Timing file has very long delays
**Solution**: 
```bash
scriptreplay --maxdelay 1.0 timing_file.txt script_file.txt
```

**Problem**: Output contains ANSI escape codes or colors
**Solution**: 
- Script(1) captures these; they replay but may look odd
- Test with scriptreplay to verify appearance

**Problem**: Session is too long (exceeds ~500 lines)
**Solution**: 
- Record multiple scripts instead of one massive one
- Keep demos focused on single concepts

---

## Modern Alternative: asciinema

For more polished recordings, consider using **asciinema** (https://asciinema.org/):

```bash
# Install asciinema
pip install asciinema

# Record
asciinema rec 01_prompt.json

# The tool uses JSON format compatible with modern players
```

Asciinema provides:
- Better timing control
- Smaller file sizes
- Direct playback in modern terminals
- Web-based sharing and editing

---

## Integration with Terminal Activity

The tutorial system automatically:
1. Locates script files in this directory based on stage definitions
2. Loads script and timing data
3. Replays using `scriptreplay(1)` into the VTE terminal
4. Manages timing and playback controls

Ensure script files match the paths referenced in `tutorial_stages.py`:
```python
script_file=_script_path("01_basics/01_prompt.txt"),
timing_file=_script_path("01_basics/01_prompt.timing"),
```

---

## Troubleshooting Recording Issues

### Script command not found
```bash
# Check if installed
which script
# Install if needed
sudo dnf install util-linux  # Fedora
sudo apt install util-linux  # Debian
```

### Timing file appears empty
- Ensure full path is provided
- Try: `script --timing=./timing_file.txt script_file.txt`

### Playback too fast
- Inspect timing file: `head -20 timing_file.txt`
- Use `scriptreplay --maxdelay 1.0` to cap delays

### Characters not echoing during recording
- This is normal for some commands
- Use `stty echo` to ensure echo mode is enabled

---

## References

- `script(1)` manual: `man script`
- `scriptreplay(1)` manual: `man scriptreplay`
- `term_escape(4)` for ANSI codes
- asciinema documentation: https://asciinema.org/docs

---

## Example Recording Session

```bash
# Create demo area
mkdir -p ~/terminal-demo
cd ~/terminal-demo

# Start recording
script --timing=01_prompt.timing 01_prompt.txt

# Now in recording:
clear
echo "=== Understanding the Command Prompt ==="
whoami
pwd
ls
echo "Done! Press Ctrl+D to exit"
# [Press Ctrl+D]

# Back to normal shell:
ls -la 01_prompt.*

# Verify timing
cat 01_prompt.timing | head -10

# Test replay
scriptreplay --maxdelay 1.0 01_prompt.timing 01_prompt.txt

# Move to scripts directory
mv 01_prompt.* /path/to/terminal-activity/scripts/01_basics/
```

---

## Contributing

When adding new tutorial stages:
1. Update `tutorial_stages.py` with stage definition
2. Record corresponding script files here
3. Follow naming convention: `NN_description.{txt,timing}`
4. Test playback thoroughly
5. Document any special considerations in comments

Questions? See [HELP_SYSTEM_DESIGN.md](../HELP_SYSTEM_DESIGN.md) for overall architecture.
