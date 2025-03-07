import subprocess
import platform
import os
import sys
import shutil

def is_ollama_installed():
    """
    Check if Ollama is installed on the system.

    Returns:
        bool: True if installed, False otherwise
    """
    try:
        result = subprocess.run(["ollama", "list"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ollama():
    """
    Install Ollama on the system.

    Returns:
        bool: True if installation successful, False otherwise
    """
    print("🔄 Installing Ollama...")

    system = platform.system().lower()

    if system == "darwin":
        # macOS
        try:
            print("⬇️ Downloading Ollama for macOS...")
            subprocess.run([
                "curl", "-fsSL", "https://ollama.com/install.sh",
                "|", "sh"
            ], shell=True, check=True)
            print("✅ Ollama installed successfully")
            return True
        except subprocess.SubprocessError:
            print("❌ Failed to install Ollama")
            return False

    elif system == "linux":
        # Linux
        try:
            print("⬇️ Downloading Ollama for Linux...")
            subprocess.run([
                "curl", "-fsSL", "https://ollama.com/install.sh",
                "|", "sh"
            ], shell=True, check=True)
            print("✅ Ollama installed successfully")
            return True
        except subprocess.SubprocessError:
            print("❌ Failed to install Ollama")
            return False

    else:
        print(f"❌ Automatic installation not supported on {system}")
        print("Please visit https://ollama.com/download for manual installation")
        return False

def has_sufficient_disk_space(required_gb=20):
    """
    Check if there's enough free disk space for the Ollama model.

    Args:
        required_gb: Required free space in GB (default: 20)

    Returns:
        bool: True if sufficient space available, False otherwise
    """
    try:
        # Get the free space on the disk where the user's home directory is located
        home_dir = os.path.expanduser("~")
        total, used, free = shutil.disk_usage(home_dir)

        # Convert to GB
        free_gb = free / (1024 ** 3)

        if free_gb < required_gb:
            print(f"⚠️ Insufficient disk space: {free_gb:.1f} GB available, {required_gb} GB required")
            print(f"Please free up at least {required_gb - free_gb:.1f} GB of disk space and try again")
            return False

        print(f"✅ Sufficient disk space available: {free_gb:.1f} GB")
        return True
    except Exception as e:
        print(f"❌ Error checking disk space: {e}")
        # In case of error, assume there's enough space to avoid blocking the user
        return True

def setup_ollama_model(model="phi4"):
    """
    Pull the specified model to Ollama.

    Args:
        model: The model to pull (default: phi4)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Make sure we have enough disk space before pulling the model
        if not has_sufficient_disk_space(required_gb=20):
            return False

        print(f"🔄 Pulling {model} model to Ollama...")
        subprocess.run(["ollama", "pull", model], check=True)
        print(f"✅ {model} model installed successfully")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print(f"❌ Failed to pull {model} model")
        return False

def check_model_exists(model="phi4"):
    """
    Check if the specified model exists in Ollama.

    Args:
        model: The model to check (default: phi4)

    Returns:
        bool: True if model exists, False otherwise
    """
    try:
        model_check = subprocess.run(
            ["ollama", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )

        return model in model_check.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def get_ai_response(prompt, model="phi4"):
    """
    Get a response from Ollama model.

    Args:
        prompt: The prompt to send to the model
        model: The model to use (default: phi4)

    Returns:
        str: Model's response or error message
    """
    try:
        print(f"🤖 Getting response from Ollama ({model})...")
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return "❌ Failed to get response from Ollama. Is Ollama installed and running?"