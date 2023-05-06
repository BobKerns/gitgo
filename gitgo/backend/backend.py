from abc import abstractmethod
import io
from typing import cast, Literal, overload, TYPE_CHECKING
from pathlib import Path
from secrets import token_hex

from gitgo.backend.base import BackendBase
from gitgo.frontend import Frontend


if TYPE_CHECKING:
    from gitgo.index import IndexEntry, FileMode
    from gitgo.object import Oid, GitObj
    from gitgo.repo import Repo
    from gitgo.worktree import Worktree
    from gitgo.objectstore import ObjectStore
    from gitgo.index import GitIndex

class Backend(BackendBase[Frontend]):
    ''''
    The Backend corresponds with a Frontend, and acts as a factry to provide
    the specific backend instances for the frontend.

    The Frontend sets the scene as director; the Backend is the stagehand moving props
    and setting up the lighting under the direction of the Frontend.
    '''
    def __init__(self, frontend: Frontend, /, **kwargs):
       super().__init__(frontend, **kwargs)
    
    @abstractmethod
    def make_repo(self, frontend: 'Repo', /, **kwargs) -> 'RepoBackend':
        ...
    
    @abstractmethod
    def make_worktree(self, frontend: 'Worktree', path: Path, /, **kwargs) -> 'WorktreeBackend':
        ...

    @abstractmethod
    def make_object_store(self, frontend: 'ObjectStore', /, **kwargs) -> 'ObjectStoreBackend':
        ...

    @abstractmethod
    def make_index(self, frontend: 'GitIndex', **kwargs) -> 'IndexBackend':
        ...

    @classmethod
    def __init_suubclass(cls):
        '''
        This is called when a subclass is created. It takes care of informing
        the front-end instance of the backend instance.
        '''
        super().__init_subclass__()
        for method in ('make_repo', 'make_worktree', 'make_object_store', 'make_index'):
            if not hasattr(cls, method):
                raise TypeError(f'{cls.__name__} must implement {method}')
            m = getattr(cls, method)
            if not callable(m):
                raise TypeError(f'{cls.__name__}.{method} must be callable')
            def wrapper(self, frontend, *args, **kwargs):
                val = m(frontend, *args, **kwargs)
                frontend.backend = val
                return val
            setattr(cls, method, wrapper)

class RepoBackend(BackendBase['Repo']):
    def __init__(self, frontend: 'Repo', /, **kwargs):
        super().__init__(frontend, **kwargs)
    @property
    @abstractmethod
    def object_store(self) -> 'ObjectStoreBackend':
        ...

class ObjectStoreBackend(BackendBase['ObjectStore']):
    def __init__(self, frontend: 'ObjectStore', /, **kwargs):
        super().__init__(frontend, **kwargs)
    
    @abstractmethod
    def fetch(self, oid: 'Oid') -> 'GitObj':
        ...
    @abstractmethod
    def store(self, oid: 'Oid', value: 'GitObj') -> None:
        ...

class IndexBackend(BackendBase['GitIndex']):
    def __init__(self, frontend: 'GitIndex', /, **kwargs):
        super().__init__(frontend, **kwargs)
    @abstractmethod
    def fetch(self, oid: 'Oid') -> 'IndexEntry':
        ...
    @abstractmethod
    def store(self, oid: 'Oid', value: 'IndexEntry') -> None:
        ...

TextModes = Literal['r', 'w', 'x', 'a', 'rw', 'rt', 'wt', 'xt', 'at', 'wrt', 'w+', 'wt+', 'r+', 'rt+']
BinaryModes = Literal['rb', 'wb', 'xb', 'ab', 'rwb', 'wb+', 'rb+']

class WorktreeBackend(BackendBase['Worktree']):
    '''
    A backend that manages a worktree.
    '''
    path: Path

    def __init__(self, frontend: 'Worktree', path: Path, /, **kwargs):
        super().__init__(frontend, **kwargs)
        self.path = path

    @abstractmethod
    def stat(self, path: Path) -> 'IndexEntry':
        stat = path.stat()
        oid = token_hex(20)
        return IndexEntry(
            name=path.name,
            type='blob',
            oid=cast(Oid, oid),
            size=stat.st_size,
            uid=stat.st_uid,
            gid=stat.st_gid,
            mode=cast(FileMode, stat.st_mode),
            ctime=stat.st_ctime,
            mtime=stat.st_mtime,
            dev = stat.st_dev,
            ino = stat.st_ino,
            flags = set(),
            )
    
    @abstractmethod
    def _open_text(self, path: Path, mode: TextModes, **kwargs) -> io.TextIOBase:
        ...

    @abstractmethod
    def _open_binary(self, path: Path, mode: BinaryModes, **kwargs) -> io.BufferedIOBase:
        ...
    
    @abstractmethod
    def _open_raw(self, path: Path, mode: str, **kwargs) -> io.IOBase:
        ...

    @overload
    def open(self, path: Path, mode: TextModes = 'r', **kwargs) -> io.TextIOBase:
        ...
    @overload
    def open(self, path: Path, mode: BinaryModes, **kwargs) -> io.BufferedIOBase:
        ...
    @overload
    def open(self, path: Path, mode: BinaryModes, *, buffering: Literal[0], **kwargs) -> io.IOBase:
        ...
    def open(self, path: Path, mode: str = 'r', *, buffering=-1, **kwargs) -> io.IOBase:
        ''''
        Open a file in the worktree.
        '''
        if 'b' in mode:
            if buffering == 0:
                return self._open_raw(path, mode, **kwargs)
            return self._open_binary(path, cast(BinaryModes,mode), buffering=buffering, **kwargs)
        else:
            return self._open_text(path, cast(TextModes,mode), buffering=buffering, **kwargs)
        