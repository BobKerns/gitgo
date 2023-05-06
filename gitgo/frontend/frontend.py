from gitgo.frontend.base import FrontendBase, T_BACKEND

class Frontend(FrontendBase[T_BACKEND]):
    backend: T_BACKEND
    def __init__(self, backend: T_BACKEND):
        self.backend = backend