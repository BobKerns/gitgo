
from typing import Optional, TYPE_CHECKING

from gitgo.frontend.base import FrontendBase
if TYPE_CHECKING:
    from gitgo.backend import ObjectStoreBackend
    from gitgo.object import Oid, GitObj

class ObjectStore(FrontendBase['ObjectStoreBackend']):
    backend: 'ObjectStoreBackend'
    _cache: dict['Oid', 'GitObj']
    def __init__(self):
        self.cache  = dict
    def __getattr__(self, oid: 'Oid') -> Optional['GitObj']:
        return self._cache.get(oid, None) or self._fetch(oid)
    def __setattr__(self, oid: 'Oid', obj: 'GitObj'):
        if oid not in self._cache:
            self._cache[oid] = obj
            self._store(oid, obj)
    
    def _fetch(self, oid: 'Oid') -> Optional['GitObj']:
        return self.backend.fetch(oid)

    def _store(self, oid: 'Oid', obj: 'GitObj'):
        self.backend.store(oid, obj)
