import os
import sys
from datetime import datetime

# Import internal modules
from ai_setup.utils.helpers import sanitize_directory_name, create_env_file, create_readme, create_makefile, init_git_repo
from ai_setup.creators.setup_files import create_ai_setup_folder, create_devlog_folder, create_docs_folder
from ai_setup.creators.work_efforts import create_work_efforts_structure, update_readme_with_work_efforts
from ai_setup.providers import ollama, openai

def create_project(project_name, ai_assisted=False, ai_provider="ollama", openai_api_key=None, ollama_model="phi4", code_dir=None):
    """
    Create a new project directory with all required files and structure.

    Args:
        project_name: Name of the project (will be sanitized for directory creation)
        ai_assisted: Whether to initialize with AI assistance
        ai_provider: 'ollama' or 'openai'
        openai_api_key: OpenAI API key if using OpenAI
        ollama_model: Model to use with Ollama
        code_dir: Optional parent directory for the project

    Returns:
        str: Path to the created project directory
    """
    # Sanitize the project name for directory creation
    dir_name = sanitize_directory_name(project_name)

    # Set the base directory
    if code_dir is None:
        code_dir = os.path.expanduser("~/Code")

    # Create the project directory
    project_dir = os.path.join(code_dir, dir_name)
    os.makedirs(project_dir, exist_ok=True)
    print(f"🎉 Project '{project_name}' created at: {project_dir}")

    # Setup project files and structure
    create_readme(project_dir, project_name)
    create_makefile(project_dir)
    create_ai_setup_folder(project_dir)
    create_devlog_folder(project_dir)
    create_docs_folder(project_dir)
    create_work_efforts_structure(project_dir)
    update_readme_with_work_efforts(project_dir)
    init_git_repo(project_dir)

    # AI-assisted mode
    if ai_assisted:
        setup_ai_assistance(project_dir, ai_provider, openai_api_key, ollama_model)

    return project_dir

def setup_ai_assistance(project_dir, ai_provider="ollama", openai_api_key=None, ollama_model="phi4"):
    """
    Set up AI assistance for the project.

    Args:
        project_dir: Project directory path
        ai_provider: 'ollama' or 'openai'
        openai_api_key: OpenAI API key if using OpenAI
        ollama_model: Model to use with Ollama
    """
    print("\n🤖 AI-Assisted Startup Initiated")

    # Create .env file with AI configuration
    create_env_file(project_dir, ai_provider, openai_api_key, ollama_model)

    if ai_provider == "ollama":
        setup_ollama_environment(ollama_model)
    elif ai_provider == "openai":
        if not openai.verify_api_key(openai_api_key):
            print("\n⚠️ Warning: The OpenAI API key format seems invalid")
            print("Please check your API key and update the .env file if needed")

    # Generate AI project planning if possible
    generate_ai_project_plan(project_dir, ai_provider, openai_api_key, ollama_model)

    print("\nAI Configuration:")
    print(f"  - Provider: {ai_provider}")
    if ai_provider == "ollama":
        print(f"  - Model: {ollama_model}")

    print("\nTo use AI assistance:")
    print("1. Open the project in an AI-powered editor like Cursor")
    print("2. Use the following files for AI assistance:")
    print(f"  - {os.path.join(project_dir, '.AI-Setup/AI-setup-instructions.md')}")
    print(f"  - {os.path.join(project_dir, '.AI-Setup/AI-work-effort-system.md')}")

def setup_ollama_environment(model="phi4"):
    """
    Set up the Ollama environment.

    Args:
        model: Ollama model to use
    """
    # Check if Ollama is installed
    if not ollama.is_ollama_installed():
        print("\n⚠️ Ollama is not installed on your system")
        install_choice = input("Would you like to install Ollama? (y/n): ")

        if install_choice.lower().startswith('y'):
            # Check for sufficient disk space before installing
            if ollama.has_sufficient_disk_space(required_gb=20):
                if ollama.install_ollama():
                    ollama.setup_ollama_model(model)
            else:
                print("\n⚠️ Installation aborted due to insufficient disk space")
        else:
            print("\n⚠️ Ollama not installed. Please install it manually from https://ollama.com/download")
    else:
        # Check if the model exists or pull it
        if not ollama.check_model_exists(model):
            setup_choice = input(f"Model {model} not found. Pull it now? (y/n): ")
            if setup_choice.lower().startswith('y'):
                # Check for sufficient disk space before pulling the model
                if ollama.has_sufficient_disk_space(required_gb=20):
                    ollama.setup_ollama_model(model)
                else:
                    print(f"\n⚠️ Model {model} installation aborted due to insufficient disk space")

def generate_ai_project_plan(project_dir, ai_provider="ollama", openai_api_key=None, ollama_model="phi4"):
    """
    Generate an AI project plan based on user's requirements.

    Args:
        project_dir: Project directory path
        ai_provider: 'ollama' or 'openai'
        openai_api_key: OpenAI API key if using OpenAI
        ollama_model: Model to use with Ollama
    """
    print("\n📋 AI Project Planning")
    description = input("\nDescribe what you want this project to do (press Enter to skip): ")

    if not description:
        print("Skipping AI project planning")
        return

    prompt = f"""You are a professional software architect and developer. You are helping to plan a new software project.
Project requirements: {description}

Please provide:
1. A high-level architecture overview
2. Key technologies and libraries to consider
3. Recommended project structure
4. Initial implementation steps
5. Potential challenges and how to address them

Keep your response concise but comprehensive."""

    # Get response from the selected AI provider
    try:
        print("\nGenerating project plan from AI...")
        if ai_provider == "ollama":
            response = ollama.get_ai_response(prompt, ollama_model)
        else:  # openai
            response = openai.get_ai_response(prompt, openai_api_key)

        # Save response to project_plan.md
        plan_path = os.path.join(project_dir, "project_plan.md")
        with open(plan_path, "w") as f:
            f.write(f"# AI-Generated Project Plan\n\n")
            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
            f.write(f"**Project Requirements:** {description}\n\n")
            f.write(f"## AI Recommendations\n\n")
            f.write(response)

        print(f"✅ AI project plan saved to: {plan_path}")
    except Exception as e:
        print(f"❌ Failed to generate AI project plan: {str(e)}")

def create_project_from_template(project_name, template_type, code_dir=None):
    """
    Create a new project from a predefined template.

    Args:
        project_name: Name of the project
        template_type: Type of template (e.g., 'python', 'node', 'react')
        code_dir: Optional parent directory for the project

    Returns:
        str: Path to the created project directory
    """
    # Create the basic project
    project_dir = create_project(project_name, code_dir=code_dir)

    # Add template-specific files
    if template_type == "python":
        setup_python_template(project_dir, project_name)
    elif template_type == "node":
        setup_node_template(project_dir)
    elif template_type == "react":
        setup_react_template(project_dir)
    else:
        print(f"⚠️ Unknown template type: {template_type}")

    return project_dir

def setup_python_template(project_dir, project_name):
    """
    Set up a Python project template.

    Args:
        project_dir: Project directory path
        project_name: Name of the project
    """
    module_name = sanitize_directory_name(project_name).replace("-", "_").lower()

    # Create package structure
    package_dir = os.path.join(project_dir, module_name)
    os.makedirs(package_dir, exist_ok=True)

    # Create __init__.py
    with open(os.path.join(package_dir, "__init__.py"), "w") as f:
        f.write(f'"""Main package for {project_name}"""\n\n__version__ = "0.4.5"\n')

    # Create main module file
    with open(os.path.join(package_dir, "main.py"), "w") as f:
        f.write(f'''"""
Main module for {project_name}
"""

def main():
    """Main entry point for the application"""
    print("Hello, world!")

if __name__ == "__main__":
    main()
''')

    # Create setup.py
    with open(os.path.join(project_dir, "setup.py"), "w") as f:
        f.write(f'''from setuptools import setup, find_packages

setup(
    name="{module_name}",
    version="0.4.5",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
    ],
)
''')

    # Create requirements.txt
    with open(os.path.join(project_dir, "requirements.txt"), "w") as f:
        f.write("# Add your dependencies here\n")

    # Update Makefile for Python
    makefile_content = """# Makefile for Python project

.PHONY: setup test clean run lint

# Default target when just running 'make'
all: setup

# Setup the project
setup:
	@echo "Setting up project dependencies..."
	pip install -e .

# Run tests
test:
	@echo "Running tests..."
	pytest

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

# Run the application
run:
	@echo "Running application..."
	python -m {module_name}

# Run linting
lint:
	@echo "Running linting..."
	flake8 {module_name}
""".format(module_name=module_name)

    with open(os.path.join(project_dir, "Makefile"), "w") as f:
        f.write(makefile_content)

    print(f"✅ Python project template set up in {project_dir}")

def setup_node_template(project_dir):
    """
    Set up a Node.js project template.

    Args:
        project_dir: Project directory path
    """
    # Create package.json
    with open(os.path.join(project_dir, "package.json"), "w") as f:
        f.write('''{
  "name": "%s",
  "version": "0.4.5",
  "description": "A Node.js project",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "test": "echo \\"Error: no test specified\\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "MIT"
}
''' % project_name)

    # Create index.js
    index_js_content = """console.log('Hello, world!');
"""

    with open(os.path.join(project_dir, "index.js"), "w") as f:
        f.write(index_js_content)

    # Update Makefile for Node.js
    makefile_content = """# Makefile for Node.js project

.PHONY: setup test clean run lint

# Default target when just running 'make'
all: setup

# Setup the project
setup:
	@echo "Setting up project dependencies..."
	npm install

# Run tests
test:
	@echo "Running tests..."
	npm test

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf node_modules/

# Run the application
run:
	@echo "Running application..."
	npm start

# Run linting
lint:
	@echo "Running linting..."
	npx eslint .
"""

    with open(os.path.join(project_dir, "Makefile"), "w") as f:
        f.write(makefile_content)

    print(f"✅ Node.js project template set up in {project_dir}")

def setup_react_template(project_dir):
    """
    Set up a React project template.

    Args:
        project_dir: Project directory path
    """
    # For React, we'll suggest using Create React App
    print("For React projects, we recommend using Create React App.")
    print("After this setup is complete, you can run:")
    print(f"cd {project_dir} && npx create-react-app .")

    # Create a simple README with instructions
    readme_content = """# React Project

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Getting Started

In the project directory, you can run:

```bash
# Install Create React App in this directory
npx create-react-app .

# Start the development server
npm start
```

## Available Scripts

In the project directory, you can run:

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App
"""

    with open(os.path.join(project_dir, "README.md"), "w") as f:
        f.write(readme_content)

    # Update Makefile for React
    makefile_content = """# Makefile for React project

.PHONY: setup test clean run build

# Default target when just running 'make'
all: setup

# Setup the project
setup:
	@echo "Setting up project dependencies..."
	npm install

# Run tests
test:
	@echo "Running tests..."
	npm test

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf node_modules/
	rm -rf build/

# Run the application
run:
	@echo "Running application..."
	npm start

# Build the application
build:
	@echo "Building application..."
	npm run build
"""

    with open(os.path.join(project_dir, "Makefile"), "w") as f:
        f.write(makefile_content)

    print(f"✅ React project template setup instructions saved to {project_dir}")