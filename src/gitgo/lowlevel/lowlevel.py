# Pythonic git interface

from pathlib import Path
from typing import Optional, Literal, overload, TextIO
from gitgo.lowlevel.cmdargs import CmdArg, CmdResult, flags, arg1s, arg2s, mkstr, \
                    exclusive, optional, enum_or_true
from gitgo.lowlevel.runner import runner
from gitgo.log import log

# Git command line interface
#
# It should be noted that this was written mostly by Copilot, and
# it is responsible for the majority of choices of what parameters
# to support. In the case of obvious errors, I have often just
# removed them, but I have not done a full review of the interface.

git = runner('git')

def git_config(flag:str, value:Optional[str] = None, /,
               is_global: bool = False,
                is_system: bool = False,
                is_local: bool = False,
                file: Optional[Path|str] = None,
                blob: Optional[str] = None,
                get: bool = False,
                get_all: bool = False,
                get_regexp: bool = False,
                get_urlmatch: bool = False,
                replace_all: bool = False,
                add: bool = False,
                unset: bool = False,
                unset_all: bool = False,
                list: bool = False,
                fixed_value: bool = False,
                null: bool = False,
                name_only: bool = False,
                show_origin: bool = False,
                show_scope: bool = False,
                type: Optional[Literal['bool', 'int', 'bool-or-int', 'path', 'expiry-date', 'color']] = None,
                default: Optional[str|int|bool|Path] = None,
                check: bool = True) -> CmdResult:
    '''
    Run git config with the given arguments.
    :param check: If True, raise an exception if the command fails
        (including 1 for NotFound).
        default: False
        '''
    file_args = arg1s(
        file=file,
        blob=blob
    )
    scope_args = (*file_args,) or \
        exclusive(
            is_global=is_global,
            is_system=is_system,
            is_local=is_local,
            file=not not file,
            blob=not not blob,
            _map={
                'is_global': 'global',
                'is_system': 'system',
                'is_local': 'local',
            }
        )
    action_args = exclusive(
        get_all=get_all,
        get=get,
        get_regexp=get_regexp,
        get_urlmatch=get_urlmatch,
        replace_all=replace_all,
        add=add,
        unset=unset,
        unset_all=unset_all,
        list=list
    )
    options = flags(
        fixed_value=fixed_value,
        null=null,
        name_only=name_only,
        show_origin=show_origin,
        show_scope=show_scope,
    )
    value_options = arg1s(
        type=type,
        default=default,
    )
    args = ("config",
            *scope_args,
            *action_args,
            *options,
            *value_options,
            flag,
            *optional(value))
    return git(*args,
               boolean_return=True,
               check=check,)

# Acceptable values for --shared parameter to git init
GitParamShared = Literal["false","true","umask","group","all","world","everybody"]|int

def git_init(directory: Path|str='.', *,
                quiet:bool=False,
                bare:bool=False,
                template:Optional[Path|str]=None,
                separate_git_dir:Optional[Path|str]=None,
                object_format:Optional[Literal["sha1","sha256"]]=None,
                branch: Optional[str]=None,
                shared: Optional[GitParamShared]=None,
                check: bool = True,
                capture_output: bool = True,
                **kwargs):
    '''
    Run git init with the given arguments.
    :param check: If True, raise an exception if the command fails
        default: True
        '''
    if type(shared) == int:
        xshared = f"0{shared:o}"
    else:
        xshared = shared
    args = ("init",
            *flags(
                quiet=quiet,
                bare=bare,
                _map={'verbose': '-v'}
            ),
            *arg1s(
                separate_git_dir=separate_git_dir,
                branch=branch,
                _map={
                    "branch": "initial-branch",
                }
            ),
            *arg2s(
                template=template,
                object_format=object_format,
                shared=xshared
            ),
            directory)
    return git(*args,
                    check=check,
                    capture_output=capture_output)

@overload
def git_checkout(branch: str, _: Optional[Literal['--']], /,
                 *paths: Path|str,
                 create: bool = False,
                reset: bool = False,
                guess: bool = False,
                quiet: bool = False,
                recurse_submodules: Optional[Literal['checkout']]|Literal[True] = None,
                progress: bool = False,
                merge: bool = False,
                conflict: Optional[Literal["diff3","merge","union"]]=None,
                detach: bool = False,
                track: Optional[bool|Literal["direct", "inherit"]]=False,
                orphan: bool = False,
                overwrite_ignore: bool = False,
                ignore_other_worktrees: bool = False,
                merge_type: Optional[Literal["merge", "ours", "theirs", "interactive"]] =None,
                 ignore_skpworktree: bool = False,
                 capture_output=True) -> CmdResult:
    '''
    Run git checkout with the given argument, including -- and paths
    '''
    ...
@overload
def git_checkout(branch: str, *,
                create: bool = False,
                reset: bool = False,
                guess: bool = False,
                quiet: bool = False,
                recurse_submodules: Optional[Literal['checkout']]|Literal[True] = None,
                progress: bool = False,
                merge: bool = False,
                conflict: Optional[Literal["diff3","merge","union"]]=None,
                detach: bool = False,
                track: Optional[bool|Literal["direct", "inherit"]]=False,
                orphan: bool = False,
                overwrite_ignore: bool = False,
                ignore_other_worktrees: bool = False,
                merge_type: Optional[Literal["merge", "ours", "theirs", "interactive"]] =None,
                ignore_skpworktree: bool = False,
                pathspec: Optional[str|Path|TextIO] = None,
                 pathspec_file_nul: bool = False,
                 capture_output=True) -> CmdResult:
    '''
    Run git checkout with the given argument, without -- or paths
    '''
    ...
def git_checkout(branch: str,
                *paths: Path|str|Optional[Literal['--']],
                create: bool = False,
                reset: bool = False,
                guess: bool = False,
                quiet: bool = False,
                recurse_submodules: Optional[Literal['checkout']]|Literal[True] = None,
                progress: bool = False,
                merge: bool = False,
                conflict: Optional[Literal["diff3","merge","union"]]=None,
                detach: bool = False,
                track: Optional[bool|Literal["direct", "inherit"]]=False,
                orphan: bool = False,
                overwrite_ignore: bool = False,
                ignore_other_worktrees: bool = False,
                merge_type: Optional[Literal["merge", "ours", "theirs", "interactive"]] =None,
                ignore_skpworktree: bool = False,
                pathspec: Optional[str|Path|TextIO] = None,
                pathspec_file_nul: bool = False,
                capture_output=True) -> CmdResult:
    '''
    Run git checkout with the given arguments.
    '''
    if len(paths) > 1 and paths[0] != '--':
        xpaths = (
            mkstr(p)
            for t in (('--'), paths)
            for p in t
            if p is not None
        )
    else:
        xpaths = (mkstr(p) for p in paths if p is not None)

    create_flag = exclusive(create=create, reset=reset, merge=merge,
                            _map={'create': '-b', 'reset': '-B', 'merge': '-m'})
    args = ("checkout", *xpaths,
            *flags(guess=guess,
                   quiet=quiet,
                   progress=progress,
                   merge=merge,
                   detach=detach,
                   orphan=orphan,
                   overwrite_ignore=overwrite_ignore,
                   ignore_other_worktrees=ignore_other_worktrees,
                   ignore_skpworktree=ignore_skpworktree,
                   pathspec_file_nul=pathspec_file_nul,
            ),
            *arg1s(
                recurse_submodules=recurse_submodules,
                conflict=conflict,
                track=track,
                merge_type=merge_type,
                pathspec=pathspec
            ),
            *create_flag,
            branch)
    return git(*args, check=True, capture_output=capture_output)


def git_credential(action: Literal['fill', 'approve', 'reject'], input: Optional[str] = None) -> str:
    '''
    Run git credential with the given arguments.
    '''
    return git("credential", action, input=input).stdout

def git_set_credentials(username: str, password: str, *,
                        url: Optional[str] = None,
                        protocol: Literal["https", "http"] = "https",
                        host: Optional[str] = None,
                        port: Optional[int] = None,
                        path: Optional[str] = None) -> None:
    '''
    Run git credential with the given arguments, to store and remember the given credentials
    in the configured credential store (e.g. ~/.git-credentials via
    git config credential.helper store)
    '''
    if url is None:
        if host == 'localhost':
            git_set_credentials(username, password,
                                 host='127.0.0.1',
                                protocol=protocol,
                                port=port,
                                path=path)
            git_set_credentials(username, password,
                                host='[::1]',
                                protocol=protocol,
                                port=port,
                                path=path)
        if host is None:
            host = "localhost"
        if path is None:
            path = "/"
        if port:
            host = f"{host}:{port}"
    pwin=f'''protocol={protocol}
host={host}
username={username}
password={password}

'''
    filled = git_credential("fill", input=pwin)
    txt = '\n'.join( (line for line in filled.split() if not line.startswith("password=")) )
    log.info(f'Credential approved for {txt}')
    git_credential('approve', input=filled)

def git_branch(branch: Optional[str] = None,
               target: Optional[str] = None,
               /,
               all: bool = False,
               create_reflog: bool = False,
               force: bool = False,
               move: bool = False,
               quiet: bool = False,
               track: bool = False,
               ignore_case: bool = False,
               set_upstream_to: Optional[str] = None,
               delete: bool = False,
               ) -> CmdResult:
    '''
    Run git branch with the given arguments.
    '''
    branch_arg = (branch,) if branch is not None else ()
    target_arg = (target,) if target is not None else ()
    args = (
       *flags(
            all=all,
            create_reflog=create_reflog,
            force=force,
            move=move,
            quiet=quiet,
            delete=delete,
            ignore_case=ignore_case,
            track=track,
            _map={
                "delete": "-d"
            }),
            '--no-color',
        *arg1s(
            set_upstream_to=set_upstream_to,
            ),
        *branch_arg,
        *target_arg,
    )
    return git("branch", *args)

def git_switch(branch: str, start: Optional[str] = None, /,
                create: bool = False,
                detach: bool = False,
                force: bool = False,
                discard_changes: bool = False,
                merge: bool = False,
                ignore_other_worktrees: bool = False,
                quiet: bool = False,
                progress: bool = False,
                track: Optional[Literal['direct', 'inherit'] ]= None,
                conflict: Optional[Literal["diff3","merge","union"]]=None,
               ) -> CmdResult:
    '''
    Run git switch with the given arguments.
    '''
    args = ("switch", branch,
            *flags(create=create,
                    force=force,
                    discard_changes=discard_changes,
                    merge=merge,
                    detach=detach,
                    track=track is not None,
                    progress=progress,
                    quiet=quiet,
                    ignore_other_worktrees=ignore_other_worktrees,
                   ),
            *arg1s(track=track,
                   conflict=conflict,))
    return git(*args)

def git_clone(url: str, path: Path|str = '.') -> CmdResult:
    '''
    Run git clone with the given arguments.
    '''
    args = ('clone', url, path)
    return git(*args)

def git_pull(*paths: CmdArg,
             remote:str = 'origin',
            branch: str = 'main',
            quiet: bool = False,
            progress: bool = False,
            force: bool = False,
            tags: bool = False,
            set_upstream: bool = False,
            dry_run: bool = False,
            rebase: bool|Literal['merges', 'interactive'] = False,
            commit: bool = True,
            ff: bool = False,
            ff_only: bool = False,
            all: bool = False,
    ) -> CmdResult:
    '''
    Run git pull with the given arguments.
    '''
    flag_args = flags(quiet=quiet,
                      progress=progress,
                      force=force,
                      tags=tags,
                      set_upstream=set_upstream,
                      dry_run=dry_run,
                      commit=commit,
                      ff=ff,
                      ff_only=ff_only,
                      all=all,)
    positional_args = (arg for arg in paths or (remote, branch) if arg is not None)
    rebase_args = arg1s(rebase=rebase)
    args = ('pull', *flag_args, *rebase_args, *positional_args)
    return git(*args)

def git_push(repo: Optional[str] = None, *refspecs: CmdArg,
                remote:str = 'origin',
                branch: Optional[str] = None,
                quiet: bool = False,
                progress: bool = False,
                force: bool = False,
                tags: bool = False,
                set_upstream: bool = False,
                dry_run: bool = False,
                rebase: bool|Literal['merges', 'interactive'] = False,
                ff: bool = False,
                ff_only: bool = False,
                all: bool = False,
                ) -> CmdResult:
    '''
    Run git push with the given arguments.
    '''
    flag_args = flags(quiet=quiet,
                      progress=progress,
                      force=force,
                      tags=tags,
                      set_upstream=set_upstream,
                      dry_run=dry_run,
                      ff=ff,
                      ff_only=ff_only,
                      all=all,)
    rebase_args = arg1s(rebase=rebase)
    positional_args  = (*optional(repo or remote), *optional(branch), *refspecs)
    args = ('push', *flag_args, *rebase_args, *positional_args)
    return git(*args)

def git_fetch(*paths: CmdArg,
                remote:str = 'origin',
                branch: str = 'main',
                quiet: bool = False,
                progress: bool = False,
                force: bool = False,
                tags: bool = False,
                set_upstream: bool = False,
                dry_run: bool = False,
                all: bool = False
                ) -> CmdResult:
    '''
    Run git fetch with the given arguments.
    '''
    flag_args = flags(quiet=quiet,
                      progress=progress,
                      force=force,
                      tags=tags,
                      set_upstream=set_upstream,
                      dry_run=dry_run,
                      all=all,)
    alt_args = (remote, branch) if branch else (remote) if remote else ()
    p_args = paths or alt_args
    positional_args = (arg for arg in p_args if arg is not None)
    args = (*flag_args, *positional_args)
    return git('fetch', *args)

@overload
def git_remote(action: Literal['add'], url_or_path: str, /,  *paths: CmdArg,
               verbose: bool = False) -> CmdResult:
    ...

@overload
def git_remote(action: Literal['add'], url_or_path: str, url: str, /,
               fetch: bool = False,
               mirror: bool = False,
               tags: bool = False,
               verbose: bool = False):
    ...

def git_remote(action: Optional[Literal['add']], url_or_path: CmdArg, /, *paths: CmdArg, **kwargs: CmdArg) -> CmdResult:
    '''
    Run git remote with the given arguments.
    '''
    args = ('remote', *optional(action), *optional(url_or_path), *paths)
    return git(*args, **kwargs)

def git_rev_parse(*args: CmdArg,
                    verify: bool = False,
                    quiet: bool = False,
                    symbolic_full_name: bool = False,
                    symbolic: bool = False,
                    abbrev_ref: bool | Literal['strict', 'loose'] = False,
                    all: bool = False,
                    branches: Optional[str] = None,
                    tags: Optional[str] = None,
                    remotes: Optional[str] = None,
                    glob: Optional[str] = None,
                    local_env_vars: bool = False,
                    path_format: Optional[Literal['absolute', 'relative']] = None,
                    git_dir: bool = False,
                    git_common_dir: bool = False,
                    resolve_git_dir: Optional[str] = None,
                    git_path: Optional[str] = None,
                    show_toplevel: bool = False,
                    show_superproject_working_tree: bool = False,
                    shared_index_path: Optional[str] = None,
                    absolute_git_dir: bool = False,
                    is_inside_git_dir: bool = False,
                    is_inside_work_tree: bool = False,
                    is_bare_repository: bool = False,
                    show_cdup: bool = False,
                    show_prefix: bool = False,
                    show_object_format: Literal['storage', 'input', 'output'] = 'storage',
                    check: bool = True,
                    capture_output: bool = True,
                  ) -> CmdResult:
    '''
    Run git rev-parse with the given arguments.
    '''
    flag_args = flags(
        verify=verify,
        quiet=quiet,
        symbolic_full_name=symbolic_full_name,
        symbolic=symbolic,
        all=all,
        local_env_vars=local_env_vars,
        git_dir=git_dir,
        git_common_dir=git_common_dir,
        show_toplevel=show_toplevel,
        show_superproject_working_tree=show_superproject_working_tree,
        absolute_git_dir=absolute_git_dir,
        is_inside_git_dir=is_inside_git_dir,
        is_inside_work_tree=is_inside_work_tree,
        is_bare_repository=is_bare_repository,
        show_cdup=show_cdup,
        show_prefix=show_prefix,
    )
    paired_args = arg1s(
        branches=branches,
        tags=tags,
        remotes=remotes,
        glob=glob,
        resolve_git_dir=resolve_git_dir,
        git_path=git_path,
        shared_index_path=shared_index_path,
        show_object_format=show_object_format,
        path_format=path_format,
    )
    abbrev_args = enum_or_true('abbrev-ref', abbrev_ref, _keywords=['strict', 'loose'])
    return git('rev-parse', *flag_args, *abbrev_args, *paired_args, *args,
               check=check,
               capture_output=capture_output)

def git_merge(*commits: CmdArg,
                abort: bool = False,
                quit: bool = False,
                continue_: bool = False,
                ff: Optional[bool|Literal['only']] = None,
                log: Optional[int] = None,
                quiet: bool = False,
                verbose: bool = False,
                no_commit: bool = False,
                progress: bool = False,
                message: Optional[str] = None,
                check: bool = True,
                capture_output: bool = True,
    ) -> CmdResult:
    '''
    Run git merge with the given arguments.
    '''
    flag_args = flags(
        abort=abort,
        quit=quit,
        continue_=continue_,
        no_commit=no_commit,
        quiet=quiet,
        verbose=verbose,
        progress=progress,
    )
    ff_flags = flags(
        ff=True if ff is True else False,
        ff_only=True if ff == 'only' else False,
    )
    params = arg1s(
        log=log,
        message=message,
    )
    args = (*ff_flags, *flag_args, *params, *commits)
    return git('merge', *args,
               check=check,
               capture_output=capture_output)

def git_tag(name: Optional[str] = None,
            commit: Optional[str] = None,
            /,
            annotate: bool = False,
            sign: bool = False,
            force: bool = False,
            message: Optional[str] = None,
            delete: bool = False,
            verify: bool = False,
            list: bool = False,
            reflog: bool = False,
    ) -> CmdResult:
    '''
    Run git tag with the given arguments.
    '''
    flag_args = flags(
        annotate=annotate,
        sign=sign,
        force=force,
        delete=delete,
        verify=verify,
        list=list,
        reflog=reflog,
    )
    params = arg1s(
        message=message,
    )
    args = (*flag_args, *params, *optional(name), *optional(commit))
    return git('tag', *args)

def git_status(*paths: CmdArg,
                porcelain: Optional[Literal['v1', 'v2']] = None,
                long: bool = False,
                short: bool = False,
                branch: bool = False,
                show_stash: bool = False,
                untracked_files: Optional[Literal['all', 'normal', 'no']] = None,
                ignored: Optional[Literal['traditional', 'no', 'matching']] = None,
                ignored_too: bool = False,
                ahead_behind: bool = False,
                find_renames: Optional[int] = None,
                renames: bool = False,
    ) -> CmdResult:
    '''
    Run git status with the given arguments.
    '''
    flag_args = flags(
        long=long,
        short=short,
        branch=branch,
        show_stash=show_stash,
        ignored_too=ignored_too,
        ahead_behind=ahead_behind,
        renames=renames,
    )
    params = arg1s(
        porcelain=porcelain,
        untracked_files=untracked_files,
        ignored=ignored,
        find_renames=find_renames,
    )
    args = (*flag_args, *params, *paths)
    return git('status', *args)
