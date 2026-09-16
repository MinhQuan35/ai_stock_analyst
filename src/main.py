"""
Forwarder to root main.py
"""
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from main import main

if __name__ == "__main__":
    main()
