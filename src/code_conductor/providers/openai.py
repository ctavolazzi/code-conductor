import os
import json
import subprocess
import sys

def verify_api_key(api_key):
    """
    Verify if the OpenAI API key is valid by making a simple test API call.
    This won't be a complete verification but checks if the key format is valid.

    Args:
        api_key: OpenAI API key

    Returns:
        bool: True if key format seems valid, False otherwise
    """
    if not api_key or len(api_key) < 20:
        return False

    # Just check basic format - starts with "sk-" and has appropriate length
    if not api_key.startswith("sk-"):
        print("⚠️ Warning: OpenAI API key should start with 'sk-'")
        return False

    return True

def check_openai_package():
    """
    Check if the OpenAI package is installed.

    Returns:
        bool: True if installed, False otherwise
    """
    try:
        subprocess.run(
            [sys.executable, "-c", "import openai"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError:
        return False

def install_openai_package():
    """
    Install the OpenAI package using pip.

    Returns:
        bool: True if installation successful, False otherwise
    """
    try:
        print("🔄 Installing OpenAI package...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "openai"],
            check=True,
            stdout=subprocess.PIPE
        )
        print("✅ OpenAI package installed successfully")
        return True
    except subprocess.SubprocessError:
        print("❌ Failed to install OpenAI package")
        return False

def get_ai_response(prompt, api_key, model="gpt-4o"):
    """
    Get a response from the OpenAI API.
    Note: This uses the subprocess way to avoid direct dependencies.

    Args:
        prompt: The prompt to send to the API
        api_key: The OpenAI API key
        model: The model to use (default: gpt-4o)

    Returns:
        str: Model's response or error message
    """
    if not check_openai_package():
        if not install_openai_package():
            return "❌ Failed to install the required OpenAI package"

    # Create a temporary Python script to make the API call
    temp_script = """
import os
import sys
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")

try:
    response = openai.chat.completions.create(
        model=sys.argv[1],
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": sys.argv[2]}
        ]
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {str(e)}")
"""

    script_path = os.path.join(os.getcwd(), "temp_openai_script.py")
    try:
        # Write the temporary script
        with open(script_path, "w") as f:
            f.write(temp_script)

        # Set environment variables and run the script
        env = os.environ.copy()
        env["OPENAI_API_KEY"] = api_key

        print(f"🤖 Getting response from OpenAI ({model})...")
        result = subprocess.run(
            [sys.executable, script_path, model, prompt],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        return result.stdout
    except subprocess.SubprocessError as e:
        return f"❌ Failed to get response from OpenAI: {str(e)}"
    finally:
        # Clean up the temporary script
        if os.path.exists(script_path):
            os.remove(script_path)