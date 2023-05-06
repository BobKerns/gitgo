from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gitgo.repo import Repo
from gitgo.frontend import FrontendBase

class Worktree(FrontendBase):
    path: Path
    repo: 'Repo'
    is_attached: bool
