from gettext import gettext as _
import os
from interactive_help import TutorialStage

_SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')


def _script_path(filename):
    return os.path.join(_SCRIPTS_DIR, filename)


class TutorialStages:

    # LEVEL 1: BASICS

    STAGE_PROMPT = TutorialStage(
        title=_("Recognizing the Prompt"),
        description=_("Every terminal session starts with a prompt, which "
                      "indicates the system is ready for input. The prompt "
                      "typically shows your username, hostname, and current "
                      "directory. It ends with $ (for regular users) or # "
                      "(for the superuser/root)."),
        script_file=_script_path("01_basics/01_prompt.txt"),
        timing_file=_script_path("01_basics/01_prompt.timing"),
        level=_("Beginner"),
        objectives=[
            _("Identify the command prompt in terminal output"),
            _("Understand prompt components: user, host, directory"),
            _("Recognize $ vs # (user vs root)")
        ]
    )
    
    STAGE_CURSOR = TutorialStage(
        title=_("The Text Cursor"),
        description=_("The text cursor is a blinking vertical line that shows "
                      "where your next typed character will appear. When you "
                      "start typing, text appears at the cursor position. You "
                      "can move the cursor using arrow keys and modify text "
                      "as needed before pressing Enter."),
        script_file=_script_path("01_basics/02_cursor.txt"),
        timing_file=_script_path("01_basics/02_cursor.timing"),
        level=_("Beginner"),
        objectives=[
            _("Locate the blinking text cursor"),
            _("Understand cursor position relative to prompt"),
            _("Use arrow keys to move cursor in a command")
        ]
    )
    
    STAGE_ECHO = TutorialStage(
        title=_("Typing Commands & Echo"),
        description=_("When you type a command, each character you type is "
                      "echoed (displayed) in the terminal as you type. This "
                      "helps you see what you're typing. After you press Enter, "
                      "the command executes and output appears below. Let's try "
                      "with 'df -h .' to see disk usage of the current directory."),
        script_file=_script_path("01_basics/03_echo.txt"),
        timing_file=_script_path("01_basics/03_echo.timing"),
        level=_("Beginner"),
        objectives=[
            _("Type a command and see it echoed"),
            _("Press Enter to execute the command"),
            _("Recognize command output vs. the prompt"),
            _("Return to a new prompt after command completion")
        ]
    )
    
    # LEVEL 2: FUNDAMENTALS
 
    STAGE_REPL = TutorialStage(
        title=_("REPL: Read-Eval-Print-Loop"),
        description=_("The terminal is a REPL: it Reads your input (command), "
                      "Evaluates it (executes), Prints the output, and loops "
                      "back to the prompt waiting for the next command. It waits "
                      "forever for input and executes exactly what you ask, "
                      "nothing more, nothing less."),
        script_file=_script_path("02_fundamentals/04_repl.txt"),
        timing_file=_script_path("02_fundamentals/04_repl.timing"),
        level=_("Beginner"),
        objectives=[
            _("Understand the Read-Eval-Print-Loop cycle"),
            _("Recognize that the terminal waits for input"),
            _("See that commands execute exactly as typed")
        ]
    )
    
    STAGE_REPEATABILITY = TutorialStage(
        title=_("Command Repeatability"),
        description=_("The terminal is deterministic and repeatable. Running "
                      "the same command with the same input will produce the "
                      "same output every time. This is fundamental to scripting "
                      "and automation. Use the up arrow (↑) to recall previous "
                      "commands and run them again."),
        script_file=_script_path("02_fundamentals/05_repeatability.txt"),
        timing_file=_script_path("02_fundamentals/05_repeatability.timing"),
        level=_("Beginner"),
        objectives=[
            _("Understand that identical commands produce identical output"),
            _("Use history recall (↑ key) to re-execute commands"),
            _("Verify repeatability by running the same command twice")
        ]
    )
    
    STAGE_PYTHON_REPL = TutorialStage(
        title=_("Python Interactive Mode"),
        description=_("Python also provides a REPL where you can enter Python "
                      "code line by line and see immediate results. This is "
                      "useful for learning, testing, and quick calculations. "
                      "Enter 'python3' to start the Python REPL and 'exit()' or "
                      "Ctrl+D to exit back to the shell."),
        script_file=_script_path("02_fundamentals/06_python_repl.txt"),
        timing_file=_script_path("02_fundamentals/06_python_repl.timing"),
        level=_("Intermediate"),
        objectives=[
            _("Start Python REPL from the terminal"),
            _("Execute Python statements interactively"),
            _("Exit Python REPL and return to shell prompt"),
            _("Understand Python's own REPL within the terminal REPL")
        ]
    )

    # LEVEL 3: ERROR HANDLING & MISTAKES
    
    STAGE_MISTAKES = TutorialStage(
        title=_("Making Mistakes & Recovery"),
        description=_("Mistakes are inevitable! Common errors include typos "
                      "('comand' instead of 'command'), permission denied "
                      "('permission denied' when running protected commands), "
                      "and 'command not found' when a command doesn't exist. "
                      "Use shell command recall (↑) and editing (← → keys, "
                      "Ctrl+A/E) to fix mistakes."),
        script_file=_script_path("03_errors/07_mistakes.txt"),
        timing_file=_script_path("03_errors/07_mistakes.timing"),
        level=_("Intermediate"),
        objectives=[
            _("Recognize common error messages"),
            _("Use history (↑) to recall previous commands"),
            _("Edit commands using arrow keys and Ctrl+A/E"),
            _("Understand what each error message means")
        ]
    )
    
    STAGE_SAFE_DELETION = TutorialStage(
        title=_("Safe Deletion Practices"),
        description=_("The 'rm' (remove) command permanently deletes files. "
                      "There is NO trash/undo! Use 'rm -i' for interactive mode, "
                      "which asks before deleting. Test with 'ls' first before "
                      "running 'rm'. Consider creating backups of important files. "
                      "This is why understanding 'rm' is critical."),
        script_file=_script_path("03_errors/08_safe_deletion.txt"),
        timing_file=_script_path("03_errors/08_safe_deletion.timing"),
        level=_("Intermediate"),
        objectives=[
            _("Understand that 'rm' permanently deletes files"),
            _("Use 'rm -i' for interactive (safe) deletion"),
            _("Use 'ls' to verify files before deletion"),
            _("Adopt safe practices to prevent accidental loss")
        ]
    )
    
    # LEVEL 4: ADVANCED TERMINAL SKILLS
    
    STAGE_COPY_PASTE = TutorialStage(
        title=_("Copying & Pasting in the Terminal"),
        description=_("Select text with your mouse by clicking and dragging. "
                      "Right-click to paste (or Ctrl+Shift+V in some terminals). "
                      "Middle-click pastes directly in some systems. This is "
                      "useful for copying commands from documentation or pasting "
                      "error messages for searching online."),
        script_file=_script_path("04_advanced/09_copy_paste.txt"),
        timing_file=_script_path("04_advanced/09_copy_paste.timing"),
        level=_("Intermediate"),
        objectives=[
            _("Select text in the terminal with the mouse"),
            _("Copy selected text to clipboard"),
            _("Paste text into terminal commands"),
            _("Use pasting for command history and documentation")
        ]
    )
    
    STAGE_LONG_OUTPUT = TutorialStage(
        title=_("Handling Long Output & Scrolling"),
        description=_("Commands like 'ls -laR' (listing all files recursively) "
                      "can produce many lines of output. Use Page Up/Page Down "
                      "to scroll, or your mouse wheel. The pipe operator '|' can "
                      "filter output. Use 'clear' to clear the screen when needed. "
                      "Learning to navigate long output is essential."),
        script_file=_script_path("04_advanced/10_long_output.txt"),
        timing_file=_script_path("04_advanced/10_long_output.timing"),
        level=_("Intermediate"),
        objectives=[
            _("Scroll through command output using Page Up/Down"),
            _("Use mouse wheel to scroll in terminal"),
            _("Use 'clear' command to clear the screen"),
            _("Understand how to return to prompt after long output")
        ]
    )
    
    STAGE_PIPING = TutorialStage(
        title=_("Piping & Output Redirection"),
        description=_("The pipe operator '|' takes output from one command and "
                      "feeds it as input to another. Redirection operators like "
                      "'>' and '>>' send output to files. For example, "
                      "'ls -l | grep .txt' filters files. 'ls > files.txt' saves "
                      "output to a file. These are powerful tools for combining "
                      "commands."),
        script_file=_script_path("04_advanced/11_piping.txt"),
        timing_file=_script_path("04_advanced/11_piping.timing"),
        level=_("Intermediate"),
        objectives=[
            _("Understand the pipe operator '|'"),
            _("Chain commands together with pipes"),
            _("Redirect output to files using '>' and '>>'"),
            _("Filter command output using grep or similar tools")
        ]
    )
    
    # LEVEL 5: USER-LEVEL TASKS
    
    STAGE_FILESYSTEM = TutorialStage(
        title=_("Filesystem Tools: cd, ls, cp, mv, rm"),
        description=_("Essential filesystem commands for managing files and "
                      "directories: 'cd' (change directory), 'ls' (list files), "
                      "'cp' (copy), 'mv' (move/rename), 'rm' (remove), 'mkdir' "
                      "(make directory), 'touch' (create file). Learn paths "
                      "(absolute vs. relative) and wildcards ('*', '?')."),
        script_file=_script_path("05_user_tasks/12_filesystem.txt"),
        timing_file=_script_path("05_user_tasks/12_filesystem.timing"),
        level=_("Intermediate"),
        objectives=[
            _("Navigate directories with 'cd'"),
            _("List files with 'ls' and its options"),
            _("Copy and move files"),
            _("Create directories and files"),
            _("Understand absolute vs. relative paths"),
            _("Use wildcards for multiple files")
        ]
    )
    
    STAGE_GUI_LAUNCH = TutorialStage(
        title=_("Starting Graphical Programs"),
        description=_("Launch GUI applications from the terminal, e.g., "
                      "'gedit myfile.txt' opens a text editor. Use '&' at the "
                      "end ('gedit &') to run in the background so the terminal "
                      "prompt returns immediately. Otherwise, the terminal waits "
                      "for the application to close."),
        script_file=_script_path("05_user_tasks/13_gui_launch.txt"),
        timing_file=_script_path("05_user_tasks/13_gui_launch.timing"),
        level=_("Intermediate"),
        objectives=[
            _("Launch graphical applications from terminal"),
            _("Use '&' to run applications in background"),
            _("Understand foreground vs. background processes"),
            _("Return to prompt while GUI app is running")
        ]
    )
    
    # LEVEL 6: SUGAR-SPECIFIC TASKS
    
    STAGE_GSETTINGS = TutorialStage(
        title=_("Sugar Settings with gsettings"),
        description=_("Sugar (the learning environment) stores settings that "
                      "can be queried and modified via 'gsettings'. Use "
                      "'gsettings list-schemas' to see available settings, "
                      "'gsettings get schema key' to read values, and "
                      "'gsettings set schema key value' to change settings. "
                      "This is useful for automation and configuration."),
        script_file=_script_path("06_sugar_tasks/14_gsettings.txt"),
        timing_file=_script_path("06_sugar_tasks/14_gsettings.timing"),
        level=_("Advanced"),
        objectives=[
            _("List available Sugar settings"),
            _("Query setting values with gsettings get"),
            _("Change settings safely with gsettings set"),
            _("Understand schema and key naming conventions")
        ]
    )
    
    STAGE_CLONE_ACTIVITY = TutorialStage(
        title=_("Cloning an Activity from GitHub"),
        description=_("Activities can be cloned from GitHub repositories using "
                      "'git clone https://github.com/owner/activity-name.git'. "
                      "After cloning, activities can be run directly from the "
                      "terminal or installed system-wide. Understanding git and "
                      "activity structure helps in development and customization."),
        script_file=_script_path("06_sugar_tasks/15_clone_activity.txt"),
        timing_file=_script_path("06_sugar_tasks/15_clone_activity.timing"),
        level=_("Advanced"),
        objectives=[
            _("Clone a GitHub repository"),
            _("Understand activity directory structure"),
            _("Navigate activity source code"),
            _("Run activities from cloned directory")
        ]
    )
    
    # LEVEL 7: SYSTEM-LEVEL TASKS
    
    STAGE_SYSTEM_INFO = TutorialStage(
        title=_("Investigating Your System"),
        description=_("Determine your system information: 'uname -a' shows "
                      "kernel details, 'lsb_release -a' shows distribution info, "
                      "'cat /etc/os-release' shows system version. These commands "
                      "help identify your OS (Fedora, Debian, etc.) which is "
                      "important for package management and troubleshooting."),
        script_file=_script_path("07_system_tasks/16_system_info.txt"),
        timing_file=_script_path("07_system_tasks/16_system_info.timing"),
        level=_("Advanced"),
        objectives=[
            _("Determine your OS and version"),
            _("Check kernel information"),
            _("Identify distribution (Fedora/Debian/etc)"),
            _("Use this info for context-appropriate commands")
        ]
    )
    
    STAGE_PACKAGE_MGMT = TutorialStage(
        title=_("Package Management: dnf vs apt"),
        description=_("Different Linux distributions use different package "
                      "managers: Fedora uses 'dnf', Debian/Ubuntu use 'apt'. "
                      "Common operations: 'dnf search package' or 'apt search "
                      "package' to find software, 'sudo dnf install package' or "
                      "'sudo apt install package' to install. Always use 'sudo' "
                      "for system-level operations."),
        script_file=_script_path("07_system_tasks/17_package_mgmt.txt"),
        timing_file=_script_path("07_system_tasks/17_package_mgmt.timing"),
        level=_("Advanced"),
        objectives=[
            _("Detect which package manager your system uses"),
            _("Search for available packages"),
            _("Install packages safely with sudo"),
            _("Understand Fedora vs Debian differences")
        ]
    )
    
    STAGE_PIP_PACKAGES = TutorialStage(
        title=_("Python Package Installation with pip"),
        description=_("Python packages are installed via 'pip' or 'pip3'. "
                      "'pip search keyword' finds packages, 'pip install package' "
                      "installs them. For system-wide installs, use 'sudo pip3 "
                      "install'. For per-user installs, use 'pip install --user'. "
                      "Virtual environments keep dependencies isolated."),
        script_file=_script_path("07_system_tasks/18_pip_packages.txt"),
        timing_file=_script_path("07_system_tasks/18_pip_packages.timing"),
        level=_("Advanced"),
        objectives=[
            _("Install Python packages with pip"),
            _("Distinguish between system and user installs"),
            _("Use virtual environments for project isolation"),
            _("Understand pip requirements files")
        ]
    )
    
    # LEVEL 8: RESOURCES & GETTING HELP
    
    STAGE_MAN_PAGES = TutorialStage(
        title=_("Finding Help: man Pages & --help"),
        description=_("Nearly all commands have built-in documentation. Use "
                      "'man command' to open the manual page (press 'q' to exit). "
                      "'command --help' or 'command -h' shows quick help. 'whatis "
                      "command' gives a one-line summary. 'apropos keyword' searches "
                      "for commands related to a keyword."),
        script_file=_script_path("08_resources/19_man_pages.txt"),
        timing_file=_script_path("08_resources/19_man_pages.timing"),
        level=_("Intermediate"),
        objectives=[
            _("Use 'man' to access command documentation"),
            _("Navigate man pages (space, q, /)"),
            _("Use '--help' flag for quick reference"),
            _("Search for commands with 'apropos'")
        ]
    )
    
    STAGE_ONLINE_HELP = TutorialStage(
        title=_("Online Documentation & Community"),
        description=_("When stuck, consult online resources: Sugar Labs "
                      "documentation (https://sugarlabs.org), Linux man pages "
                      "online (https://linux.die.net), Stack Overflow for "
                      "programming questions, and community forums. Google your "
                      "error message! Sharing error output helps others help you."),
        script_file=_script_path("08_resources/20_online_help.txt"),
        timing_file=_script_path("08_resources/20_online_help.timing"),
        level=_("Intermediate"),
        objectives=[
            _("Know Sugar Labs documentation resources"),
            _("Access online Linux man pages"),
            _("Search effectively for solutions"),
            _("Share errors appropriately in forums")
        ]
    )
    
    @classmethod
    def get_all_stages(cls):
        """Return list of all tutorial stages in order."""
        return [
            # Basics
            cls.STAGE_PROMPT,
            cls.STAGE_CURSOR,
            cls.STAGE_ECHO,
            # Fundamentals
            cls.STAGE_REPL,
            cls.STAGE_REPEATABILITY,
            cls.STAGE_PYTHON_REPL,
            # Error Handling
            cls.STAGE_MISTAKES,
            cls.STAGE_SAFE_DELETION,
            # Advanced Skills
            cls.STAGE_COPY_PASTE,
            cls.STAGE_LONG_OUTPUT,
            cls.STAGE_PIPING,
            # User Tasks
            cls.STAGE_FILESYSTEM,
            cls.STAGE_GUI_LAUNCH,
            # Sugar Tasks
            cls.STAGE_GSETTINGS,
            cls.STAGE_CLONE_ACTIVITY,
            # System Tasks
            cls.STAGE_SYSTEM_INFO,
            cls.STAGE_PACKAGE_MGMT,
            cls.STAGE_PIP_PACKAGES,
            # Resources
            cls.STAGE_MAN_PAGES,
            cls.STAGE_ONLINE_HELP,
        ]
    
    @classmethod
    def get_stages_by_level(cls, level):
        all_stages = cls.get_all_stages()
        return [s for s in all_stages if s.level == level]
