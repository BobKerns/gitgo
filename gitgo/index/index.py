from dataclasses import dataclass, field
from typing import Iterator, overload, Generic, Optional, Literal, Set, TYPE_CHECKING

from gitgo.frontend import FrontendBase

if TYPE_CHECKING:
    from gitgo.backend import RepoBackend
from gitgo.object import Oid, T_IndexType, ObjIType

# ruff: noqa: E501

Ellipsis = type(...)

FileMode = Literal[0o755, 0o644, 0]

Idx_Flag = Literal['assume-valid', 'skip-worktree', 'intent-to-add']

Timestamp = float

@dataclass
class IndexEntry(Generic[T_IndexType]):
    '''
    An entry in a Git index file.
    '''
    name: str
    type: T_IndexType
    oid: Oid
    mode: FileMode
    ctime: Timestamp
    mtime: Timestamp
    dev: int
    ino: int
    uid: int
    gid: int
    flags: Set[Idx_Flag]
    size: int

_Index_Version = Literal[2, 3, 4]

_Stage = dict[Oid, IndexEntry[ObjIType]]
_Stages = tuple[_Stage, _Stage, _Stage, _Stage]
_Entries = tuple[
        Optional[IndexEntry[ObjIType]],
        Optional[IndexEntry[ObjIType]],
        Optional[IndexEntry[ObjIType]],
        Optional[IndexEntry[ObjIType]]
    ]
_Stage_idx = Literal[0, 1, 2, 3]
_Stage_oid = tuple[_Stage_idx, Oid]
_Ellipse_oid = tuple[Ellipsis, Oid]  # How could I resist this name?

@dataclass
class GitIndex(FrontendBase):
    '''
    A Git index file. This is a four-stage index, with the following
    semantics:
    - Stage 0: the working tree that was checked out
    - Stage 1: On a merge, the common ancestor.
    - stage 2: On a merge, the LEFT commit (typically this branch)
    - stage 3: the RIGHT commit (typically the other branch)

    The index is keyed by (stage, oid), where stage is 0, 1, 2, or 3.
    i.e.:

    index[0, oid] = entry for the working tree
    index[1, oid] = entry for the common ancestor
    index[2, oid] = entry for the LEFT commit in a merge
    index[3, oid] = entry for the RIGHT commit in a merge
    index[..., oid] = (index[0, oid], index[1, oid], index[2, oid], index[3, oid])

    The stage is defauilted to 0, so index[oid] is equivalent to
    index[0, oid].

    Stage 0 and stages 1-3 are mutually exclusive for a particular file.
    Thit is, if a file is in stage 0, it cannot be in any of stages 1-3,
    and vice versa.
    '''
    backend: 'RepoBackend'
    _stages: _Stages = field(init=False, default_factory=lambda : (  
        dict(),
        dict(),
        dict(),
        dict()
    ))

    version: _Index_Version = field(default=3, kw_only=True)

    def __post_init__(self) -> None:
        '''
        Validate the supplied data.
        '''
        if self.version not in (2, 3, 4):
            raise ValueError(f'Invalid index version {self.version}')
    
    @overload
    def __getitem__(self, name: Oid, /) -> Optional[IndexEntry[ObjIType]]:
        ...
    @overload
    def __getitem__(self, sidx: _Stage_oid, /) -> Optional[IndexEntry[ObjIType]]:
        ...
    @overload
    def __getitem__(self, idx: _Ellipse_oid, /) -> _Entries:
        ...
    def __getitem__(self, name_or_idx: Oid|_Stage_oid|_Ellipse_oid, /) -> \
            Optional[IndexEntry[ObjIType]] \
            | _Entries:
        stages = self._stages
        match (name_or_idx):
            case Oid() as oid:
                return stages[0].get(oid, None)
            case (0|1|2 as idx, Oid() as oid):
                return stages[idx].get(oid, None)
            case (Ellipsis(), Oid() as oid):
                return (
                    stages[0].get(oid, None),
                    stages[1].get(oid, None),
                    stages[2].get(oid, None),
                    stages[3].get(oid, None)
                )                  
            case _:
                raise AttributeError(f'No such attribute: {name_or_idx}')
    def __delitem__(self, idx: Oid|_Stage_oid|_Ellipse_oid, /) -> None:
        stages = self._stages
        match (idx):
            case Oid() as oid:
                del stages[0][oid]
                del stages[1][oid]
                del stages[2][oid]
                del stages[3][oid]
            case (0|1|2|3 as sidx, Oid() as oid):
                del stages[sidx][oid]
            case (Ellipsis(), Oid() as oid):
                del stages[0][oid]
                del stages[1][oid]
                del stages[2][oid]
                del stages[3][oid]
            case _:
                raise AttributeError(f'No such attribute: {idx}')

    @overload
    def __setitem__(self, oid: Oid, entry: IndexEntry[ObjIType], /) -> None:
        ...
    @overload
    def __setitem__(self, stage: _Stage_oid, entry: IndexEntry[ObjIType], /) -> None:
        ...
    @overload
    def __setitem__(self, idx: _Ellipse_oid, entry: _Entries, /) -> None:
        ...
    def __setitem__(self, 
                    idx: Oid|_Stage_oid|_Ellipse_oid,
                    entry: IndexEntry[ObjIType] | _Entries
                    ) -> None:
        stages = self._stages
        match (idx):
            case (1|2|3 as sidx, Oid() as oid):
                if not isinstance(entry, IndexEntry):
                    raise TypeError(f'Expected IndexEntry, got {type(entry)}')
                stages[sidx][oid] = entry
                del stages[0][oid]
            case (Ellipsis(), Oid() as oid):
                if oid in stages[0] and (
                    oid in stages[1] or
                    oid in stages[2] or
                    oid in stages[3]
                ):
                    msg = f'Cannot set index entry for {oid} in stage 0 and stages 1-3'
                    raise ValueError(msg)
                if not isinstance(entry, tuple) \
                    or len(entry) != 4 \
                    or not all(isinstance(e, IndexEntry) for e in entry):
                    raise TypeError(f'Expected 4-tuple of IndexEntry, got {type(entry)}')
                for s, e in zip(stages, entry):
                    if e is None:
                        del s[oid]
                    else:
                        s[oid] = e
            case Oid() as oid:
                if not isinstance(entry, IndexEntry):
                    raise TypeError(f'Expected IndexEntry, got {type(entry)}')
                self[..., oid] = (entry, None, None, None)
            case (0, Oid() as oid):
                if not entry:
                    del stages[0][oid]
                elif not isinstance(entry, IndexEntry):
                    raise TypeError(f'Expected IndexEntry, got {type(entry)}')
                else:
                    stages[0][oid] = entry
                    for s in stages[1:]:
                        del s[oid]
            case _:
                raise AttributeError(f'No such attribute: {idx}')
    def __iter__(self) -> Iterator[tuple[_Stage_idx, IndexEntry[ObjIType]]]:
        return iter(
            (i, v)
            for i in (0, 1, 2, 3)
            for v in self._stages[i].values()
        )
            
    def ls_files(self, unmerged:bool = False):
        '''
        Return a Set of the the files in the index.
        '''
        stages = (0, 1, 2, 3) if unmerged else (0,)
        return {
            e.name
            for i in stages
            for e in self._stages[i].values()
        }
    
    def len(self) -> int:
        '''
        Return the number of entries in the index.
        '''
        return sum(len(s) for s in self._stages)

@dataclass
class GitPhysIndex(GitIndex):
    '''
    A Git index file on the filesystem.
    '''
    path: str
