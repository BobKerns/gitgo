from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from gitgo.backend import ObjectStoreBackend
from gitgo.frontend import FrontendBase
if TYPE_CHECKING:
    from gitgo.repo import Repo
    from gitgo.object import Oid, GitObj

@dataclass
class ObjectStore(FrontendBase[ObjectStoreBackend]):
    repo: 'Repo'
    backend: ObjectStoreBackend
    _cache: dict['Oid', 'GitObj'] = field(default_factory=dict)
    def __getattr__(self, oid: 'Oid') -> Optional['GitObj']:
        return self._cache.get(oid, None) or self._fetch(oid)
    def __setattr__(self, oid: 'Oid', obj: 'GitObj'):
        if oid not in self._cache:
            self._cache[oid] = obj
            self._store(oid, obj)
    
    def _fetch(self, oid: 'Oid') -> Optional['GitObj']:
        return self.repo.backend.object_store.fetch(oid)

    def _store(self, oid: 'Oid', obj: 'GitObj'):
        self.repo.backend.object_store.store(oid, obj)
