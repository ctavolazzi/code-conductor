import os
import re
import subprocess
from datetime import datetime

def sanitize_directory_name(name):
    """
    Convert a user input string into a valid directory name.

    Args:
        name: String input from user

    Returns:
        Sanitized string valid for directory name
    """
    # Replace spaces with hyphens and remove special characters
    sanitized = re.sub(r'[^\w\s-]', '', name).strip()
    sanitized = re.sub(r'[-\s]+', '-', sanitized)

    if not sanitized:
        sanitized = "new-project"  # Default if name is empty after sanitization

    return sanitized

def create_env_file(project_dir, ai_provider="ollama", openai_api_key=None, ollama_model="phi4"):
    """
    Create .env file with AI configuration in the project directory.

    Args:
        project_dir: Project directory path
        ai_provider: 'ollama' or 'openai'
        openai_api_key: OpenAI API key (if provider is openai)
        ollama_model: Ollama model to use (if provider is ollama)
    """
    env_content = f"# AI Setup Configuration\n"
    env_content += f"AI_PROVIDER={ai_provider}\n"

    if ai_provider == "ollama":
        env_content += f"OLLAMA_MODEL={ollama_model}\n"
        env_content += f"OLLAMA_HOST=http://localhost:11434\n"
    elif ai_provider == "openai":
        env_content += f"OPENAI_API_KEY={openai_api_key}\n"
        env_content += f"OPENAI_MODEL=gpt-4\n"

    env_file_path = os.path.join(project_dir, ".env")
    with open(env_file_path, "w") as env_file:
        env_file.write(env_content)

    # Add .env to .gitignore if it exists
    gitignore_path = os.path.join(project_dir, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            content = f.read()

        if ".env" not in content:
            with open(gitignore_path, "a") as f:
                f.write("\n# Environment variables\n.env\n")
    else:
        with open(gitignore_path, "w") as f:
            f.write("# Environment variables\n.env\n")

    print(f"✅ Created .env file with {ai_provider} configuration")

def create_readme(project_dir, project_name):
    """
    Create a basic README.md file in the project directory.

    Args:
        project_dir: Project directory path
        project_name: Name of the project
    """
    readme_content = f"""# {project_name}

Project created on {datetime.now().strftime('%Y-%m-%d')}

## Overview
Add your project description here.

## Setup
Instructions for setting up the project.

## Usage
How to use the project.
"""

    with open(os.path.join(project_dir, "README.md"), "w") as f:
        f.write(readme_content)

    print(f"✅ Created README.md file")

def create_makefile(project_dir):
    """
    Create a basic Makefile in the project directory.

    Args:
        project_dir: Project directory path
    """
    makefile_content = """# Makefile for project management

.PHONY: setup test clean run

# Default target when just running 'make'
all: setup

# Setup the project
setup:
	@echo "Setting up project dependencies..."
	# Add your setup commands here

# Run tests
test:
	@echo "Running tests..."
	# Add your test commands here

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the application
run:
	@echo "Running application..."
	# Add your run command here
"""

    with open(os.path.join(project_dir, "Makefile"), "w") as f:
        f.write(makefile_content)

    print(f"✅ Created Makefile")

def init_git_repo(project_dir):
    """
    Initialize a Git repository in the project directory.

    Args:
        project_dir: Project directory path

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        subprocess.run(["git", "init"], cwd=project_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ Initialized git repository")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("⚠️ Failed to initialize git repository - git might not be installed")
        return False