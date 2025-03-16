import sys
import os

# Add parent directory to path to allow direct imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import directly from __init__.py
from __init__ import __version__
