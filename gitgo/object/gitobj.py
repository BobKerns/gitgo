
from dataclasses import dataclass
import re
from typing import NewType, TypeGuard

from gitgo.objectstore import ObjectStore

Oid = NewType('Oid', str)

RE_OID = re.compile(r'^[0-9a-f]$')
def is_oid(oid: str) -> TypeGuard[Oid]:
    return (
        len(oid) == 40 or len(oid) == 64
    ) and RE_OID.match(oid) is not None

@dataclass
class GitObj:
    '''
    Any object in a Git repository object store.
    '''
    store: ObjectStore
    oid: Oid