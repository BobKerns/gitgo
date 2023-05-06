### Null backend

from pathlib import Path
import io

from gitgo.backend import Backend, BackendBase, RepoBackend, ObjectStoreBackend, WorktreeBackend, IndexBackend, \
    TextModes, BinaryModes
from gitgo.frontend import Frontend
from gitgo.repo import Repo
from gitgo.worktree import Worktree
from gitgo.objectstore import ObjectStore
from gitgo.index import GitIndex

class NullBackendBase(BackendBase):
    ...

class NullBackend(Backend, NullBackendBase):
    def __init__(self, frontend: Frontend, /, **kwargs):
       super().__init__(frontend, **kwargs)
    
    def make_repo(self, frontend: Repo, /, **kwargs) -> RepoBackend:
        backend = NullRepoBackend(frontend, **kwargs)
        frontend.backend = backend
        return backend
    
    def make_worktree(self, frontend: Worktree, path: Path, /, **kwargs) -> WorktreeBackend:
        backend = NullWorktreeBackend(frontend, path, **kwargs)
        frontend.backend = backend
        return backend

    def make_object_store(self, frontend: ObjectStore, /, **kwargs) -> ObjectStoreBackend:
        ...

    def make_index(self, frontend: GitIndex, **kwargs) -> IndexBackend:
        ...

class NullRepoBackend(RepoBackend, NullBackendBase):
    ...

class NullObjectStoreBackend(ObjectStoreBackend, NullBackendBase):
    ...

class NullIndexBackend(IndexBackend, NullBackendBase):
    ...

class NullWorktreeBackend(WorktreeBackend, NullBackendBase):
    def __init__(self, frontend: Worktree, path: Path, /, **kwargs):
        super().__init__(frontend, path, **kwargs)

    def _open_text(self, path: Path, mode: TextModes, **kwargs) -> io.TextIOBase:
        return io.StringIO()

    def _open_binary(self, path: Path, mode: BinaryModes, **kwargs) -> io.BufferedIOBase:
        return io.BytesIO()
    
    def _open_raw(self, path: Path, mode: str, **kwargs) -> io.IOBase:
        return io.BytesIO()

