### Null backend

from pathlib import Path
import io

from gitgo.backend import Backend, BackendBase, RepoBackend, ObjectStoreBackend, WorktreeBackend, IndexBackend, \
    TextModes, BinaryModes

class NullBackendBase(BackendBase):
    ...

class NullBackend(Backend, NullBackendBase):
    def __init__(self, /, **kwargs):
       super().__init__(**kwargs)
    
    def make_repo(self, /, **kwargs) -> RepoBackend:
       return  NullRepoBackend(**kwargs)
    
    def make_worktree(self, path: Path, /, **kwargs) -> WorktreeBackend:
        return NullWorktreeBackend(path, **kwargs)

    def make_object_store(self, /, **kwargs) -> ObjectStoreBackend:
        return NullObjectStoreBackend(**kwargs)

    def make_index(self, **kwargs) -> IndexBackend:
        return NullIndexBackend(**kwargs)

class NullRepoBackend(RepoBackend, NullBackendBase):
    ...

class NullObjectStoreBackend(ObjectStoreBackend, NullBackendBase):
    ...

class NullIndexBackend(IndexBackend, NullBackendBase):
    ...

class NullWorktreeBackend(WorktreeBackend, NullBackendBase):
    def __init__(self, path: Path, /, **kwargs):
        super().__init__(path, **kwargs)

    def _open_text(self, path: Path, mode: TextModes, **kwargs) -> io.TextIOBase:
        return io.StringIO()

    def _open_binary(self, path: Path, mode: BinaryModes, **kwargs) -> io.BufferedIOBase:
        return io.BytesIO()
    
    def _open_raw(self, path: Path, mode: str, **kwargs) -> io.IOBase:
        return io.BytesIO()

