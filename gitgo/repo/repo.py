from typing import List, Optional
from dataclasses import dataclass
from typing import NewType
from pathlib import Path
from gitgo.worktree import Worktree
from gitgo.ref import GitRef
from gitgo.backend import BackendRepo

@dataclass
class Repo:
    ''''
    Any Git repository, local or remote.
    '''
    backend: BackendRepo
    refs: dict[str, GitRef]

GitUrl = NewType('GitUrlStr', str) | NewType('GitUrlPath', Path)

class RemoteRepo(Repo):
    '''
    A local model of a remote Git repository. A local git repo can be associated with
    multiple remote repos. A remote repo has a subset of the information
    available: local versions of remote refs, and a path or URL to the
    physical remote repo, which can be queried for more refs or objects.

    A remote repo may have an associated local repo, if we have physical
    access to it. Two local repos may even have each other as remotes.
    A remote repo is a local repo's limited model of the state of the
    remote repo, updated through the 'fetch' and 'push' operations.
    '''
    url: GitUrl
    local_repo: Optional['LocalRepo'] = None

@dataclass
class LocalRepo(Repo):
    '''
    A repository on our local filesystem. A local repo has a path to the
    physical repo, and a list of worktrees. IT may also have a list of
    remote repos that it can pull changes from and/or push changes to.

    A local repo may have multiple worktrees, but only one of them
    contains the .git directory. The other worktrees are "linked" to the
    main worktree, and are called "linked worktrees". They are
    distinguished from "detached worktrees", which are worktrees that
    have their own .git directory.

    Only local repos can gi ve us full GitObj objects.
    '''
    path: Path
    worktrees: List[Worktree]
    remotes: dict[str, 'RemoteRepo']



