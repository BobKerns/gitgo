from dataclasses import dataclass
from typing import Optional

from gitgo.repo import Repo
from gitgo.object import Oid, GitObj
from gitgo.backend.backend import BackendObjectStore

@dataclass
class ObjectStore:
    repo: Repo
    backend: BackendObjectStore
    _cache: dict[Oid, GitObj] = dict()
    def __getattr__(self, oid: Oid) -> Optional[GitObj]:
        return self._cache.get(oid, None) or self._fetch(oid)
    def __setattr__(self, oid: Oid, obj: GitObj):
        if oid not in self._cache:
            self._cache[oid] = obj
            self._store(oid, obj)
    
    def _fetch(self, oid: Oid) -> Optional[GitObj]:
        return self.repo.backend.object_store.fetch(oid)

    def _store(self, oid: Oid, obj: GitObj):
        self.repo.backend.object_store.store(oid, obj)
