from pathlib import Path

from repo import Repo

class Worktree:
    path: Path
    repo: Repo
    is_attached: bool
