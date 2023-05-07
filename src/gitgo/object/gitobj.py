
from dataclasses import dataclass
import re
from typing import NewType, TypeGuard, Literal, TypeVar

from gitgo.objectstore import ObjectStore

Oid = NewType('Oid', str)

'''
A git object type for types that can appear in the index.
'''
ObjIType = Literal['blob', 'symlink', 'gitlink', 'module']

'''
Any Git object that can be stored in the objectstare
'''
ObjType = Literal['tree', 'commit', 'tag'] | ObjIType

'''
Type variable constrained to any Git object type
(i.e. objects that can appear in the object store)
'''
T_ObjType = TypeVar('T_ObjType', bound=ObjType)

# Typevar for Object types that can appear in the index.
T_IndexType = TypeVar('T_IndexType', bound=ObjIType)


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
    _store: ObjectStore
    oid: Oid
    type: ObjType

    def __str__(self) -> str:
        return self.oid
    
    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.oid})'
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GitObj):
            return False
        return self.oid == other.oid
    
    # Make them sortable, with no particular semantics.
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, GitObj):
            return False
        return self.oid < other.oid
    
    def __hash__(self) -> int:
        '''
        Hash based on the OID.
        
        The type is included in the hash making up the Oid.
        '''
        return hash(self.oid)

class GitBlob(GitObj):
    '''
    A Git blob object.
    '''
    type: Literal['blob']
    def __init__(self, store: ObjectStore, oid: Oid):
        super().__init__(store, oid, 'blob')

class GitTree(GitObj):
    '''
    A Git tree object.
    '''
    type: Literal['tree']
    def __init__(self, store: ObjectStore, oid: Oid):
        super().__init__(store, oid, 'tree')

class GitCommit(GitObj):
    '''
    A Git commit object.
    '''
    type: Literal['commit']
    def __init__(self, store: ObjectStore, oid: Oid):
        super().__init__(store, oid, 'commit')

class GitAnnotatedTag(GitObj):
    '''
    An annitated Git tag object.
    '''
    type: Literal['tag']
    def __init__(self, store: ObjectStore, oid: Oid):
        super().__init__(store, oid, 'tag')

class GitTag(GitObj):
    '''
    A Git tag object.
    '''
    type: Literal['tag']
    def __init__(self, store: ObjectStore, oid: Oid):
        super().__init__(store, oid, 'tag')

class GitModule(GitObj):
    '''
    A Git submodule object.
    '''
    type: Literal['module']
    def __init__(self, store: ObjectStore, oid: Oid):
        super().__init__(store, oid, 'module')

class GitSymlink(GitObj):
    '''
    A Git symlink object.
    '''
    type: Literal['symlink']
    def __init__(self, store: ObjectStore, oid: Oid):
        super().__init__(store, oid, 'symlink')

class GitGitlink(GitObj):
    '''
    A Git gitlink object.
    '''
    type: Literal['gitlink']
    def __init__(self, store: ObjectStore, oid: Oid):
        super().__init__(store, oid, 'gitlink') 
