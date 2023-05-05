from abc import ABCMeta, abstractmethod
from typing import cast
from pathlib import Path
from object import Oid, GitObj
from index import IndexEntry, FileMode

class Backend:
    ...

class BackendRepo(Backend, metaclass=ABCMeta):
    @property
    @abstractmethod
    def object_store(self) ->'BackendObjectStore':
        ...


class BackendObjectStore(Backend, metaclass=ABCMeta):
    @abstractmethod
    def fetch(self, oid: Oid) -> GitObj:
        ...
    @abstractmethod
    def store(self, oid: Oid, value: GitObj) -> None:
        ...

class WorktreeBackend(Backend, metaclass=ABCMeta):
    '''
    A backend that manages a worktree.
    '''

    @abstractmethod
    def fetch(self, path: Path) -> IndexEntry:
        stat = path.stat()
        oid = 'fake-oid',
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