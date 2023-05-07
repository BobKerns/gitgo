from typing import TYPE_CHECKING
from pathlib import Path

from gitgo.frontend.base import FrontendBase
from gitgo.repo import Repo
from gitgo.worktree import Worktree
from gitgo.objectstore import ObjectStore
from gitgo.index import GitIndex

if TYPE_CHECKING:
    from gitgo.backend import Backend

class Frontend(FrontendBase['Backend']):
    def __init__(self, backend: 'Backend'):
        self.backend = backend
        backend.frontend = self

    def make_repo(self, path: Path, /, *, bare: bool = False) -> 'Repo':
        repo = Repo()
        self.backend.make_repo(repo, path=path, bare=bare)
        return repo
    
    def make_worktree(self, repo: 'Repo', path: Path, /, *, is_attached: bool = False) -> 'Worktree':
        worktree = Worktree()
        self.backend.make_worktree(worktree, path, is_attached=is_attached)
        return worktree
    
    def make_object_store(self, repo: 'Repo', /) -> 'ObjectStore':
        store = ObjectStore()
        self.backend.make_object_store(store)
        return store
    
    def make_index(self, /) -> 'GitIndex':
        index = GitIndex()
        self.backend.make_index(index)
        return index
    