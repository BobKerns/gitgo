from typing import List, Optional
from pathlib import Path

from gitgo.repo import Repo

class Worktree:
    path: Path
    #repo: Repo
    is_attached: bool