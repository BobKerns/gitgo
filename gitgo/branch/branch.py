
from gitgo.ref import GitRef
from gitgo.repo import Repo

class Branch(GitRef):
    '''
    A branch is a ref that is a child of refs/heads/.
    The refs/heads/ namespace is where names that are
    expected to name branches will be found by their
    simple name.
    '''
    def __init__(self, repo: Repo, name: str):
        super().__init__(repo, 'refs/heads/', name)
    def __repr__(self):
        return f"{self.name}@{self.repo}"
        