'''Utility functions for environment management.'''

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

def load_env(env_file: Optional[str] = None) -> None:
    '''Load environment variables from a .env file.

    :param env_file: Optional custom path to the .env file. If not
        provided, the function searches for a .env file in the current
        working directory and its parents.
    '''
    if env_file:
        load_dotenv(dotenv_path=env_file, override=False)
        return
    # Walk up the directory tree to find a .env file
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        candidate = parent / '.env'
        if candidate.exists():
            load_dotenv(dotenv_path=candidate, override=False)
            return
    # No .env found; do nothing
