from abc import abstractmethod
import io
from typing import cast, Literal, overload, TYPE_CHECKING
from pathlib import Path
from secrets import token_hex

from gitgo.backend.base import T_FRONTEND, BackendBase

if TYPE_CHECKING:
    from gitgo.index import IndexEntry, FileMode
    from gitgo.object import Oid, GitObj
    from gitgo.repo import Repo  # noqa: F401
    from gitgo.worktree import Worktree  # noqa: F401
    from gitgo.objectstore import ObjectStore  # noqa: F401
    from gitgo.index import GitIndex  # noqa: F401
    from gitgo.frontend import Frontend  # noqa: F401

class Backend(BackendBase['Frontend']):
    ''''
    The Backend corresponds with a Frontend, and acts as a factory to provide
    the specific backend instances for the frontend.

    The Frontend sets the scene as director; the Backend is the stagehand moving props
    and setting up the lighting under the direction of the Frontend.
    '''
    def __init__(self, /, **kwargs):
       super().__init__(**kwargs)
    
    @abstractmethod
    def make_repo(self,repo: 'Repo', /, **kwargs) -> 'RepoBackend':
        ...
    
    @abstractmethod
    def make_worktree(self, tree: 'Worktree', path: Path, /, **kwargs) -> 'WorktreeBackend':
        ...

    @abstractmethod
    def make_object_store(self, store: 'ObjectStore', /, **kwargs) -> 'ObjectStoreBackend':
        ...

    @abstractmethod
    def make_index(self, index: 'GitIndex', **kwargs) -> 'IndexBackend':
        ...

    @classmethod
    def __init_subclass__(cls,  /, **kwargs):
        '''
        This is called when a subclass is created. It takes care of informing
        the front-end instance of the backend instance.
        '''
        super().__init_subclass__(**kwargs)

        print(f'__init_subclass__ called for {cls.__name__}')
        for method in ('make_repo', 'make_worktree', 'make_object_store', 'make_index'):
            m = getattr(cls, method)
            def wrapper(self, frontend: T_FRONTEND, *args, **kwargs) -> T_FRONTEND:
                print(f'wrapper called for {cls.__name__}.{method}')
                val = m(self, *args, **kwargs)
                frontend.backend = val
                val.frontend = frontend
                return val
            setattr(cls, method, wrapper)

class RepoBackend(BackendBase['Repo']):
    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)
    @property
    @abstractmethod
    def object_store(self) -> 'ObjectStoreBackend':
        ...

class ObjectStoreBackend(BackendBase['ObjectStore']):
    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)
    
    @abstractmethod
    def fetch(self, oid: 'Oid') -> 'GitObj':
        ...
    @abstractmethod
    def store(self, oid: 'Oid', value: 'GitObj') -> None:
        ...

class IndexBackend(BackendBase['GitIndex']):
    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)
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

    def __init__(self, path: Path, /, **kwargs):
        super().__init__(**kwargs)
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
        