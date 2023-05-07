from typing import Generic, TypeVar, TYPE_CHECKING
if TYPE_CHECKING:
    from gitgo.backend import BackendBase

T_BACKEND = TypeVar('T_BACKEND', bound='BackendBase')


class FrontendBase(Generic[T_BACKEND]):
    '''
    Base class for frontend objects, i.e.
    objects that communicate with a corresponding
    backend object.'''
    backend: 'T_BACKEND'
