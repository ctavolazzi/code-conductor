import json
import asyncio
import requests
import random
import sys
from typing import Optional

# ANSI escape codes for terminal manipulation
CLEAR_LINE = "\033[K"
UP_ONE_LINE = "\033[F"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

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
            self.current_line += char
            self._write_text(self.current_line)
            await asyncio.sleep(random.uniform(min_delay, max_delay))

    async def simulate_thinking(self, text: str):
        """Simulate thinking with dots."""
        base_text = text
        for _ in range(3):
            for i in range(4):
                dots = "." * i
                self._write_text(f"{base_text}{dots}")
                await asyncio.sleep(0.3)

    async def simulate_erasing(self, delay: float = 0.05):
        """Simulate erasing text character by character."""
        while self.current_line:
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

async def generate_content_with_ollama(description: str, model: str = "phi3") -> Optional[dict]:
    """Generate content for the work effort using Ollama with thought process simulation."""
    print("🧠 Starting content generation process...")

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

        # Make the actual API call with streaming enabled
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": True},
            stream=True
        )

        full_response = ""
        first_token = True

        for line in response.iter_lines():
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
    except Exception as e:
        print(f"\n❌ Error communicating with Ollama: {e}")
    finally:
        # Ensure thought process is stopped
        simulator.should_continue = False
        await thought_process

    return None

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