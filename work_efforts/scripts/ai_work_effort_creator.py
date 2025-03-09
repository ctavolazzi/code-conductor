import os
import argparse
import json
import asyncio
import requests
import random
import sys
import time
import signal
from datetime import datetime
from typing import Optional

# Get the absolute path to the work-efforts directory
WORK_EFFORTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(WORK_EFFORTS_DIR, "templates", "work-effort-template.md")
ACTIVE_PATH = os.path.join(WORK_EFFORTS_DIR, "active")

# ANSI escape codes for terminal manipulation
CLEAR_LINE = "\033[K"
UP_ONE_LINE = "\033[F"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

# Default timeout for AI content generation (in seconds)
DEFAULT_TIMEOUT = 30

# Simulated thought process messages for different phases
PLANNING_THOUGHTS = [
    ("Analyzing work effort description...", "Understanding context and requirements..."),
    ("Identifying key objectives...", "Extracting main goals from description..."),
    ("Formulating tasks...", "Breaking down objectives into actionable items..."),
    ("Considering dependencies...", "Mapping relationships between tasks..."),
    ("Evaluating complexity...", "Assessing effort required for each task...")
]

GENERATION_THOUGHTS = [
    ("Generating objectives...", "Crafting clear and actionable goals..."),
    ("Defining tasks...", "Creating specific implementation steps..."),
    ("Writing contextual notes...", "Adding relevant background details..."),
    ("Refining language...", "Ensuring clarity and precision..."),
    ("Structuring output...", "Formatting content for readability...")
]

FINAL_THOUGHTS = [
    ("Validating content...", "Checking completeness and coherence..."),
    ("Organizing workflow...", "Structuring tasks in logical sequence..."),
    ("Finalizing response...", "Preparing formatted output...")
]

# Flag to indicate if we should abort the AI generation
abort_requested = False

def signal_handler(sig, frame):
    global abort_requested
    abort_requested = True
    print("\n⚠️ Aborting AI content generation...")

class ThoughtProcessSimulator:
    def __init__(self):
        self.should_continue = True
        self.current_line = ""
        self.generation_started = asyncio.Event()
        self.current_phase = "planning"  # planning, generating, finalizing

    def _erase_current_line(self):
        """Erase the current line in the terminal."""
        sys.stdout.write(CLEAR_LINE)
        sys.stdout.write('\r')
        sys.stdout.flush()

    def _write_text(self, text: str):
        """Write text to the current line."""
        self._erase_current_line()
        sys.stdout.write('\r' + text)
        sys.stdout.flush()

    async def simulate_typing(self, text: str, min_delay: float = 0.02, max_delay: float = 0.1):
        """Simulate typing text character by character."""
        for char in text:
            if not self.should_continue:
                return
            self.current_line += char
            self._write_text(self.current_line)
            await asyncio.sleep(random.uniform(min_delay, max_delay))

    async def simulate_thinking(self, text: str):
        """Simulate thinking with dots."""
        base_text = text
        for _ in range(3):
            if not self.should_continue:
                return
            for i in range(4):
                if not self.should_continue:
                    return
                dots = "." * i
                self._write_text(f"{base_text}{dots}")
                await asyncio.sleep(0.3)

    async def simulate_erasing(self, delay: float = 0.05):
        """Simulate erasing text character by character."""
        while self.current_line and self.should_continue:
            self.current_line = self.current_line[:-1]
            self._write_text(self.current_line)
            await asyncio.sleep(delay)

    def signal_generation_started(self):
        """Signal that token generation has started."""
        self.generation_started.set()

    async def run_thought_process(self):
        """Run the main thought process simulation."""
        print("\n")  # Start with a blank line
        sys.stdout.write(HIDE_CURSOR)

        try:
            while self.should_continue:
                # Planning phase thoughts
                if not self.generation_started.is_set():
                    thoughts = PLANNING_THOUGHTS
                else:
                    # Switch to generation thoughts when tokens start flowing
                    thoughts = GENERATION_THOUGHTS

                for thought, alternative in thoughts:
                    if not self.should_continue:
                        break

                    # Type out first thought
                    await self.simulate_typing(thought)
                    await self.simulate_thinking(thought)
                    await self.simulate_erasing()

                    # Type out alternative thought
                    await self.simulate_typing(alternative)
                    await self.simulate_thinking(alternative)
                    await self.simulate_erasing()

                    # Check if generation has started
                    if not self.generation_started.is_set():
                        try:
                            await asyncio.wait_for(self.generation_started.wait(), 0.1)
                        except asyncio.TimeoutError:
                            continue

                # If we've completed the generation thoughts, move to final thoughts
                if self.generation_started.is_set():
                    for thought, alternative in FINAL_THOUGHTS:
                        if not self.should_continue:
                            break
                        await self.simulate_typing(thought)
                        await self.simulate_thinking(thought)
                        await self.simulate_erasing()

        finally:
            sys.stdout.write(SHOW_CURSOR)
            self._erase_current_line()
            sys.stdout.flush()

async def generate_content_with_ollama(description: str, model: str = "phi3", timeout: int = DEFAULT_TIMEOUT) -> Optional[dict]:
    """Generate content for the work effort using Ollama with thought process simulation."""
    global abort_requested
    abort_requested = False  # Reset at the start of each generation

    print("🧠 Starting content generation process...")
    print(f"⏱️  Timeout set to {timeout} seconds. Press Ctrl+C to abort.")
    print("💡 Content generation will proceed in background. You can work on other tasks.")

    # Set up the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start the thought process simulator
    simulator = ThoughtProcessSimulator()
    thought_process = asyncio.create_task(simulator.run_thought_process())

    try:
        prompt = f"""
        Based on this description: "{description}"

        Please generate structured content for a work effort. Provide:

        1. 3-5 clear objectives (bullet points)
        2. 4-6 specific tasks (as checklist items with "- [ ]" format)
        3. 2-3 contextual notes (bullet points)

        Format the response as a valid JSON object with keys: "objectives", "tasks", and "notes".
        Keep the content concise and focused.
        """

        # Function to handle timeout
        async def handle_timeout():
            await asyncio.sleep(timeout)
            global abort_requested
            if not abort_requested:
                abort_requested = True
                print("\n⏱️ Timeout reached. Aborting AI content generation...")

        # Start the timeout handler
        timeout_task = asyncio.create_task(handle_timeout())

        try:
            # Make the actual API call with streaming enabled
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": True},
                stream=True
            )

            full_response = ""
            first_token = True

            for line in response.iter_lines():
                if abort_requested:
                    break

                if line:
                    # Signal generation has started on first token
                    if first_token:
                        simulator.signal_generation_started()
                        first_token = False

                    try:
                        data = json.loads(line)
                        if "response" in data:
                            full_response += data["response"]
                    except json.JSONDecodeError:
                        continue

            # Cancel the timeout task
            timeout_task.cancel()

            if abort_requested:
                simulator.should_continue = False
                await thought_process
                print("\n🛑 AI content generation aborted. Using template defaults.")
                return None

            try:
                # Find JSON object in the response
                start_idx = full_response.find('{')
                end_idx = full_response.rfind('}') + 1

                if start_idx >= 0 and end_idx > start_idx:
                    json_str = full_response[start_idx:end_idx]
                    content = json.loads(json_str)

                    # Stop the thought process and show success
                    simulator.should_continue = False
                    await thought_process
                    print("\n✨ Content generated successfully!")
                    return content
                else:
                    print("\n❌ Could not extract valid JSON from model response.")
            except json.JSONDecodeError:
                print("\n❌ Could not parse model response as JSON.")
        finally:
            # Ensure the timeout task is cancelled
            timeout_task.cancel()

    except Exception as e:
        print(f"\n❌ Error communicating with Ollama: {e}")
    finally:
        # Ensure thought process is stopped
        simulator.should_continue = False
        await thought_process
        # Reset signal handler
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    return None

# Function to support creating work efforts in the current directory
def get_active_directory(use_current_dir=False):
    """Get the directory where the work effort should be created.

    Args:
        use_current_dir: If True, use the current working directory

    Returns:
        Path to the directory where the work effort should be created
    """
    if use_current_dir:
        current_dir = os.getcwd()
        # Create a work_efforts/active directory in the current directory if it doesn't exist
        work_efforts_dir = os.path.join(current_dir, "work_efforts")
        active_dir = os.path.join(work_efforts_dir, "active")
        templates_dir = os.path.join(work_efforts_dir, "templates")

        # Create required directories
        os.makedirs(active_dir, exist_ok=True)
        os.makedirs(templates_dir, exist_ok=True)

        return active_dir
    return ACTIVE_PATH

def get_template_path(use_current_dir=False):
    """Get the path to the template file, creating it if necessary.

    Args:
        use_current_dir: If True, use a template in the current directory

    Returns:
        Path to the template file
    """
    if use_current_dir:
        current_dir = os.getcwd()
        templates_dir = os.path.join(current_dir, "work_efforts", "templates")
        local_template_path = os.path.join(templates_dir, "work-effort-template.md")

        # If the template doesn't exist in the current directory, copy it from the package
        if not os.path.exists(local_template_path):
            # Create the template file if it doesn't exist
            with open(TEMPLATE_PATH, "r") as src_template:
                template_content = src_template.read()

            with open(local_template_path, "w") as dest_template:
                dest_template.write(template_content)

            print(f"Created template file at: {local_template_path}")

        return local_template_path
    return TEMPLATE_PATH

def create_work_effort(title, assignee, priority, due_date, content=None, use_current_dir=False):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename_timestamp = datetime.now().strftime("%Y%m%d%H%M")
    filename = f"{filename_timestamp}_{title.lower().replace(' ', '_')}.md"

    # Get the appropriate active directory and template path
    active_dir = get_active_directory(use_current_dir)
    template_path = get_template_path(use_current_dir)
    file_path = os.path.join(active_dir, filename)

    with open(template_path, "r") as template_file:
        template_content = template_file.read()

    # Replace template variables
    filled_content = template_content.replace("{{title}}", title)
    filled_content = filled_content.replace("{{status}}", "active")
    filled_content = filled_content.replace("{{priority}}", priority)
    filled_content = filled_content.replace("{{assignee}}", assignee)
    filled_content = filled_content.replace("{{created}}", timestamp)
    filled_content = filled_content.replace("{{last_updated}}", timestamp)
    filled_content = filled_content.replace("{{due_date}}", due_date)

    # If AI-generated content is provided, replace the placeholders
    if content:
        if "objectives" in content:
            filled_content = filled_content.replace("- Clearly define goals for this work effort.", content["objectives"])
        if "tasks" in content:
            filled_content = filled_content.replace("- [ ] Task 1\n- [ ] Task 2", content["tasks"])
        if "notes" in content:
            filled_content = filled_content.replace("- Context, links to relevant code, designs, references.", content["notes"])

    with open(file_path, "w") as new_file:
        new_file.write(filled_content)

    print(f"\n🚀 New work effort created at: {file_path}")
    return file_path

def get_available_ollama_models():
    """Get a list of available Ollama models."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        return ["phi3", "llama3", "mistral"]  # Fallback defaults if can't get models
    except Exception as e:
        print(f"⚠️ Could not connect to Ollama: {e}")
        return ["phi3", "llama3", "mistral"]  # Fallback defaults

def parse_arguments():
    parser = argparse.ArgumentParser(description="Create a new work effort")
    parser.add_argument("--title", default="Untitled", help="Title of the work effort (default: Untitled)")
    parser.add_argument("--assignee", default="self", help="Assignee of the work effort (default: self)")
    parser.add_argument("--priority", default="medium", choices=["low", "medium", "high", "critical"],
                        help="Priority of the work effort (default: medium)")
    parser.add_argument("--due-date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Due date in YYYY-MM-DD format (default: today)")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run in interactive mode (prompt for values)")
    parser.add_argument("--use-ai", action="store_true",
                        help="Use AI to generate content (OFF by default)")
    parser.add_argument("--description",
                        help="Description of the work effort (for content generation with --use-ai)")
    parser.add_argument("--model", default="phi3",
                        help="Ollama model to use for content generation (with --use-ai)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        help=f"Timeout in seconds for AI content generation (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--current-dir", action="store_true",
                        help="Create work effort in current directory (default: False)")
    return parser.parse_args()

# Non-async entry point for the console script
def main():
    """Entry point for the console script."""
    asyncio.run(main_async())

# The async main function
async def main_async():
    args = parse_arguments()
    ai_content = None

    if args.interactive:
        print("Create a New Work Effort (press Enter for default values):")

        # Get user input with defaults
        title_input = input(f"Enter title [{args.title}]: ")
        title = title_input if title_input.strip() else args.title

        assignee_input = input(f"Enter assignee [{args.assignee}]: ")
        assignee = assignee_input if assignee_input.strip() else args.assignee

        priority_input = input(f"Enter priority (low, medium, high, critical) [{args.priority}]: ")
        priority = priority_input if priority_input.strip() else args.priority

        due_date_input = input(f"Enter due date (YYYY-MM-DD) [{args.due_date}]: ")
        due_date = due_date_input if due_date_input.strip() else args.due_date

        use_current_dir_input = input("Create in current directory? (y/N): [default: NO] ")
        use_current_dir = use_current_dir_input.lower() in ('y', 'yes')

        # Ask if user wants to use AI content generation
        use_ai_input = input("Use AI to generate content? (y/N): [default: NO] ")
        use_ai = use_ai_input.lower() in ('y', 'yes')

        if use_ai:
            # Ask for description for AI content generation
            description_input = input("Enter a description for AI content generation: ")

            if description_input.strip():
                timeout_input = input(f"Enter timeout in seconds [{args.timeout}]: ")
                timeout = int(timeout_input) if timeout_input.strip().isdigit() else args.timeout

                available_models = get_available_ollama_models()

                if available_models:
                    default_model = "phi3" if "phi3" in available_models else available_models[0]
                    print(f"Available models: {', '.join(available_models)}")
                    model_input = input(f"Choose a model [{default_model}]: ")
                    model = model_input if model_input.strip() and model_input in available_models else default_model

                    ai_content = await generate_content_with_ollama(description_input, model, timeout)
                else:
                    print("⚠️ No Ollama models available. Using template defaults.")
    else:
        # Use command-line arguments directly
        title = args.title
        assignee = args.assignee
        priority = args.priority
        due_date = args.due_date
        use_current_dir = args.current_dir

        # Only use AI if specifically requested with --use-ai flag
        if args.use_ai and args.description:
            ai_content = await generate_content_with_ollama(args.description, args.model, args.timeout)

        # If no arguments were provided (using defaults), assume the user wants it in the current directory
        if (title == "Untitled" and assignee == "self" and
            priority == "medium" and due_date == datetime.now().strftime("%Y-%m-%d") and
            not args.use_ai and not args.current_dir):
            use_current_dir = True
            print("No options specified, creating default work effort in current directory.")

        print(f"Creating work effort with title: {title}, assignee: {assignee}, priority: {priority}, due date: {due_date}")
        if use_current_dir:
            print("Creating in current working directory")

    create_work_effort(title, assignee, priority, due_date, ai_content, use_current_dir)

if __name__ == "__main__":
    asyncio.run(main_async())