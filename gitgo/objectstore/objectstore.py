from dataclasses import dataclass
from typing import Optional

from gitgo.repo import Repo
from gitgo.object import Oid, GitObj

@dataclass
class ObjectStore:
    repo: Repo
    _cache: dict[Oid, GitObj] = dict()
    def __getattr__(self, oid: Oid) -> Optional[GitObj]:
        return self._cache.get(oid, None) or self._fetch(oid)
    def __setattr__(self, oid: Oid, obj: GitObj):
        if not oid in self._cache:
            self._cache[oid] = obj
            self._store(oid, obj)
    
    def _fetch(self, oid: Oid) -> Optional[GitObj]:
        return self.repo.backend.object_store.fetch(oid)

    def _store(self, oid: Oid, obj: GitObj):
        self.repo.backend.object_store.store(oid, obj)
        