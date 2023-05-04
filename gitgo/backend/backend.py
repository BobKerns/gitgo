from abc import ABCMeta, abstractmethod
from gitgo.object import Oid, GitObj

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
