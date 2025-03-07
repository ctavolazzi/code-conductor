import os
import sys
import shutil
from typing import List, Set, Tuple

# Check if running on Windows or Unix-like system
if os.name == 'nt':  # Windows
    import msvcrt
else:  # Unix-like
    import termios
    import tty

# ANSI escape codes
CLEAR_SCREEN = '\033[2J\033[H' if os.name != 'nt' else ''
CURSOR_UP = '\033[A' if os.name != 'nt' else ''
CLEAR_LINE = '\033[2K' if os.name != 'nt' else ''
CURSOR_TO_COL = '\033[G' if os.name != 'nt' else ''
SAVE_CURSOR = '\033[s' if os.name != 'nt' else ''
RESTORE_CURSOR = '\033[u' if os.name != 'nt' else ''
HIDE_CURSOR = '\033[?25l' if os.name != 'nt' else ''
SHOW_CURSOR = '\033[?25h' if os.name != 'nt' else ''
CYAN = '\033[96m' if os.name != 'nt' else ''
GREEN = '\033[92m' if os.name != 'nt' else ''
YELLOW = '\033[93m' if os.name != 'nt' else ''
BOLD = '\033[1m' if os.name != 'nt' else ''
RESET = '\033[0m' if os.name != 'nt' else ''

def create_ai_setup(root_dir=None):
    """Create the .AI-setup folder structure with all necessary files."""
    if root_dir is None:
        root_dir = os.getcwd()

    # Define the AI setup folder
    setup_folder = os.path.join(root_dir, ".AI-Setup")

    # Create .AI-Setup folder
    if not os.path.exists(setup_folder):
        os.makedirs(setup_folder)

    # Create required files
    instructions_file = os.path.join(setup_folder, "INSTRUCTIONS.md")
    with open(instructions_file, "w") as f:
        f.write("""# AI-Setup Instructions

This directory contains setup files for AI-assisted development.

## Usage

This setup enables your AI assistants to better understand your project structure
and provide more contextual help and recommendations.

No action is required from you - the AI tools will automatically utilize these files.
""")

    print(f"✅ Created AI-Setup in: {root_dir}")
    return setup_folder

def install_ai_setup(target_dirs):
    """Install AI-Setup in target directories."""
    # Create a temporary .AI-Setup in the current directory
    temp_dir = os.getcwd()
    setup_folder = create_ai_setup(temp_dir)

    # Copy to selected directories
    for directory in target_dirs:
        # Skip if directory doesn't exist
        if not os.path.exists(directory) or not os.path.isdir(directory):
            print(f"❌ Directory not found: {directory}")
            continue

        # Skip if already installed
        if is_ai_setup_installed(directory):
            print(f"⚠️ AI-Setup already installed in: {directory}")
            continue

        # Create .AI-Setup in target directory
        target_setup = os.path.join(directory, ".AI-Setup")
        if not os.path.exists(target_setup):
            os.makedirs(target_setup)

        # Copy all files from temporary .AI-Setup to target
        for item in os.listdir(setup_folder):
            source = os.path.join(setup_folder, item)
            target = os.path.join(target_setup, item)
            if os.path.isfile(source):
                shutil.copy2(source, target)

        print(f"✅ Installed AI-Setup in: {directory}")

    # Clean up temporary .AI-Setup if it was created for this operation
    if setup_folder != os.path.join(temp_dir, ".AI-Setup"):
        shutil.rmtree(setup_folder)

def is_ai_setup_installed(directory: str) -> bool:
    """Check if AI-Setup is already installed in a directory."""
    if not os.path.exists(directory) or not os.path.isdir(directory):
        return False

    return os.path.exists(os.path.join(directory, ".AI-Setup"))

def get_directories(base_dir: str = ".") -> List[str]:
    """
    Get valid directories in the base directory.

    Args:
        base_dir: Base directory to scan

    Returns:
        List[str]: List of directory names
    """
    try:
        # Get all items in the directory
        items = os.listdir(base_dir)

        # Filter for directories, exclude hidden ones and special directories
        directories = [
            item for item in items
            if os.path.isdir(os.path.join(base_dir, item))
            and not item.startswith('.')
            and not item.endswith('.egg-info')
            and item not in ['__pycache__', 'node_modules', 'venv', '.venv', 'env', '.env']
        ]

        # Ensure no duplicates by converting to set and back to list
        unique_directories = sorted(set(directories))

        # Debug information
        if len(unique_directories) != len(directories):
            print(f"Note: Removed {len(directories) - len(unique_directories)} duplicate directory entries")

        return unique_directories
    except Exception as e:
        print(f"❌ Error scanning directory: {str(e)}")
        return []

def clear_screen():
    """Clear the screen in a cross-platform way."""
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Unix/Linux/MacOS
        os.system('clear')  # Use os.system instead of ANSI codes for more reliability

def draw_menu_item(idx, directory, is_selected, is_current, has_ai_setup):
    """Draw a single menu item with proper formatting."""
    prefix = f"{BOLD}➤{RESET}" if is_current else " "
    checkbox = f"[{GREEN}✓{RESET}]" if is_selected else "[ ]"
    ai_setup_status = f" {CYAN}(AI-Setup installed){RESET}" if has_ai_setup else ""

    # Highlight the current item
    directory_text = f"{YELLOW}{directory}{RESET}" if is_current else directory

    return f"{prefix} {checkbox} {directory_text}{ai_setup_status}"

def print_directory_menu(directories, selected, current_idx, visible_range=None, redraw=False):
    """
    Print the interactive directory selection menu.
    Always does a full redraw for reliability.

    Args:
        directories: List of directory names
        selected: Set of selected directory names
        current_idx: Index of the currently highlighted directory
        visible_range: Tuple of (start_idx, end_idx) for visible range
        redraw: Not used, kept for compatibility
    """
    # Always clear the screen for reliability
    clear_screen()

    if visible_range is None:
        # Default to showing all directories
        visible_range = (0, len(directories))

    start_idx, end_idx = visible_range

    # Print header
    print(f"{BOLD}📂 Directory Selection{RESET}")
    print(f"Found {len(directories)} directories in: {os.getcwd()}")
    print(f"Use {CYAN}↑/↓{RESET} to navigate | {CYAN}SPACE{RESET} to select | {CYAN}ENTER{RESET} to confirm | {CYAN}'a'{RESET} to select all | {CYAN}ESC/q{RESET} to quit")
    print()

    # Print all visible directory items
    for idx in range(start_idx, min(end_idx, len(directories))):
        directory = directories[idx]
        is_selected = directory in selected
        is_current = idx == current_idx
        has_ai_setup = is_ai_setup_installed(os.path.join(os.getcwd(), directory))

        print(draw_menu_item(idx, directory, is_selected, is_current, has_ai_setup))

    # Print scroll indicators if needed
    if start_idx > 0:
        print(f"{CYAN}↑ More directories above{RESET}")
    if end_idx < len(directories):
        print(f"{CYAN}↓ More directories below{RESET}")

    print(f"\nSelected: {len(selected)}/{len(directories)}")

    # Ensure output is displayed immediately
    sys.stdout.flush()

def get_key():
    """Get a keypress from the user in a cross-platform way."""
    if os.name == 'nt':  # Windows
        # Windows needs special handling for arrow keys
        key = msvcrt.getch()
        if key == b'\xe0':  # Special keys
            key = msvcrt.getch()
            if key == b'H': return 'up'
            if key == b'P': return 'down'
            return 'special'
        elif key == b'\r': return '\r'  # Enter
        elif key == b' ': return ' '    # Space
        elif key == b'\x1b': return '\x1b'  # Escape
        elif key == b'a' or key == b'A': return 'a'
        elif key == b'q' or key == b'Q': return 'q'
        return key.decode('utf-8', errors='ignore')
    else:  # Unix-like
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # Escape sequence
                ch = sys.stdin.read(1)
                if ch == '[':  # CSI sequence for arrow keys
                    ch = sys.stdin.read(1)
                    if ch == 'A': return 'up'
                    if ch == 'B': return 'down'
                    if ch == 'C': return 'right'
                    if ch == 'D': return 'left'
                return '\x1b'  # Just Escape
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def select_directories(base_dir=None):
    """
    Interactive directory selection with optimized UI updates.

    Args:
        base_dir: Base directory to scan for subdirectories

    Returns:
        List[str]: List of selected directory paths
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # Get directories in the current path
    directories = get_directories(base_dir)
    if not directories:
        print("❌ No valid directories found in", base_dir)
        return []

    # Initialize selection state
    selected = set()
    current_idx = 0

    # Determine viewport size (how many items to show at once)
    try:
        terminal_height = os.get_terminal_size().lines
        max_visible = min(terminal_height - 8, len(directories))  # Leave room for header and footer
    except (OSError, AttributeError):
        max_visible = min(15, len(directories))  # Fallback if terminal size can't be determined

    # Initial viewport range
    start_idx = 0
    end_idx = min(start_idx + max_visible, len(directories))
    visible_range = (start_idx, end_idx)

    try:
        # Initial draw
        print_directory_menu(directories, selected, current_idx, visible_range)

        while True:
            key = get_key()

            if key in ['q', '\x1b']:  # q or ESC to quit
                clear_screen()  # Clear screen before exiting
                print("❌ Operation cancelled")
                return []

            elif key == ' ':  # Space to toggle selection
                if directories:  # Ensure there are directories to select
                    dir_name = directories[current_idx]
                    if dir_name in selected:
                        selected.remove(dir_name)
                    else:
                        selected.add(dir_name)
                    # Always do a full redraw for reliability
                    print_directory_menu(directories, selected, current_idx, visible_range)

            elif key == 'a':  # 'a' to select/deselect all
                if len(selected) == len(directories):
                    selected.clear()
                else:
                    selected = set(directories)
                # Full redraw
                print_directory_menu(directories, selected, current_idx, visible_range)

            elif key == '\r':  # Enter to confirm selection
                if not selected:
                    print("\n\n❌ No directories selected")
                    continue

                # Clear screen before showing confirmation
                clear_screen()

                # Get full paths for selected directories
                selected_paths = [os.path.join(base_dir, d) for d in selected]

                # Show confirmation and install
                print("✅ Selected directories:")
                for path in selected_paths:
                    print(f"  - {os.path.basename(path)}")

                print("\n🚀 Installing AI-Setup to selected directories...")
                install_ai_setup(selected_paths)
                return selected_paths

            elif key == 'up' and current_idx > 0:
                # Move up in the list
                current_idx -= 1

                # Adjust viewport if needed
                if current_idx < start_idx:
                    start_idx = max(0, current_idx - max_visible // 2)
                    end_idx = min(len(directories), start_idx + max_visible)
                    visible_range = (start_idx, end_idx)

                # Always do a full redraw for reliability
                print_directory_menu(directories, selected, current_idx, visible_range)

            elif key == 'down' and current_idx < len(directories) - 1:
                # Move down in the list
                current_idx += 1

                # Adjust viewport if needed
                if current_idx >= end_idx:
                    start_idx = max(0, current_idx - max_visible // 2)
                    end_idx = min(len(directories), start_idx + max_visible)
                    visible_range = (start_idx, end_idx)

                # Always do a full redraw for reliability
                print_directory_menu(directories, selected, current_idx, visible_range)

    finally:
        # Make sure we leave the terminal in a clean state
        pass

    return []