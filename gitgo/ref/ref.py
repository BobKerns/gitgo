from typing import Optional, NewType

from gitgo.repo import Repo

SymbolicRef = NewType('SymbolicRef', str)

class GitRef:
    '''
    A GitRef is a reference to a Git object, denoted by a SHA-1 or SHA-256 hash.
    '''
    repo: Repo
    name: str
    path: str
    def __init__(self, repo: Repo, path_or_prefix: str, name: Optional[str] = None):
        self.repo = repo
        if name:
            self.name = name
            self.path = f'{path_or_prefix}/{name}'
        else:
            self.path = path_or_prefix
            self.name = self.path.split('/')[-1]

    def __str__(self):
        return self.path

    def __repr__(self):
        return f"{self.path}@{self.repo}"