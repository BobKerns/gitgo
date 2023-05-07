from typing import Generic, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from gitgo.frontend import FrontendBase

T_BACKEND = TypeVar('T_BACKEND', bound='BackendBase')
T_FRONTEND = TypeVar('T_FRONTEND', bound='FrontendBase')

class BackendBase(Generic[T_FRONTEND]):
    '''
    Base class for backend objects.
    
    Backend objects are objects that are associated with a frontend object,
    and provide a specific implementation of the functionality for the
    front end. For example, a backend object may provide a specific
    implementation of the object store, or the index, or the worktree. 
    
    This will can be handed off to ``git`` itself, or be emulated, or actions
    can be tracked and turned into a script'''
    frontend: T_FRONTEND

    def __init__(self, /, **kwargs):
        super().__init__(**kwargs)
