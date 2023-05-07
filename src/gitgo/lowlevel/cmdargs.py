from typing import Generator, Optional, Callable, Any, cast, Tuple, NamedTuple
from pathlib import Path

# The type of thing we can pass to commands
CmdArg = str | Path | int | float | bool

class CmdResult(NamedTuple):
    stdout: str
    stderr: str
    returncode: int | bool

def mkstr(v: Optional[CmdArg]) -> str:
    '''
    Return a string representation of the given value for Git.
    '''
    match v:
        case None:
            raise ValueError('None not allowed')
        case str():
                return cast(str, v)
        case Path():
            return str(v)
        case bool():
            return str(v).lower()
        case _:
            return str(v)

def mkflg(k: str, _map: dict[str, str])  -> str:
    '''
    Return a flag of the form "-flag". _map is consulted to remap
    the flag name. If the remapped value starts with '-' it is used
    literally. Otherwise, "--" is prepended. Underscores are automatically
    remapped to dashes. To override this, supply the correct value in _map.
    '''
    k = _map.get(k, k.replace('_', '-'))
    if k.startswith('-'):
        return k
    else:
        return f'--{k}'


def flags(*, _map: dict[str, str] = {}, **kwargs) -> Generator[str, None, None]:
    '''
    Return a gemeratpr of flags of the form "-flag" from the given map
    and kwargs. The value of the kwarg can be anything truthy. If falsey,
    the flag is not included.
    :param _map: is a dictionary mapping argument names to flag names.
    '''
    return (mkflg(k, _map) for k, v in kwargs.items() if v)

def negated(*, _map: dict[str, str] = {}, **kwargs) -> Generator[str, None, None]:
    '''
    Return a gemeratpr of negated flags of the form "-no-flag" from the given
    map and kwargs. The value of the kwarg can be anything Falsey. If truthy,
    the flag is not included.
    :param _map: is a dictionary mapping argument names to flag names.
    '''
    return (f'--no-{_map.get(k , k.replace("_", "-"))}'
            for k, v in kwargs.items()
            if not v)

def exclusive(_required:bool =False,
                _map:dict[str,str] = {},
                **kwargs: bool):
    exclusive = {n:v for n, v in dict(**kwargs).items()
                  if v}
    if len(exclusive) > 1:
        raise ValueError(f'Only one of {exclusive.keys()} may be specified.')
    if _required and not exclusive:
        raise ValueError(f'One of {kwargs.keys()} must be specified.')
    return flags(_map=_map, **exclusive)

def conditional(value, **kwargs) -> dict[str,CmdArg]:
    if value:
        return kwargs
    else:
        return {}

def optional(value, default=None) -> Tuple[CmdArg]:
    if value == default:
        return tuple()
    else:
        return (value,)

def arg1s(*,
          _map: dict[str, str] = {},
          _omit: Callable[[str, Any], bool] = lambda k, v: not v,
          **kwargs) -> Generator[str, None, None]:
    '''
    Return a generator of arguments of the form "--name=value" from the give
    keyword arguments.

    By default, if value is falsey, the argument is not included. If this is a
    problem, supply a different _omit function.

    :param _map: is a dictionary mapping argument names to flag names.
    :param _omit: is a function of (key, value) that returns True if the argument should be
        omitted. By default, this is true if the value is falsey.
        key is the unmapped name of the argument, value is the value of the argument.
    '''
    return (f'{mkflg(k, _map)}={mkstr(v)}'
            for k, v in kwargs.items()
            if not _omit(k, v))


def enum_or_true(key: str, value: Any, *,
            _keywords: list[str],
            _map: dict[str, str] = {},
            _omit: Callable[[str, Any], bool] = lambda k, v: not v,
            **kwargs) -> Generator[str, None, None]:
    '''
    Return a generator of arguments of the form "--name=value" from the give
    keyword arguments. If the value is

    By default, if value is falsey, the argument is not included. If this is a
    problem, supply a different _omit function.

    :param _map: is a dictionary mapping argument names to flag names.
    :param _omit: is a function of (key, value) that returns True if the argument should be
        omitted. By default, this is true if the value is falsey.
        key is the unmapped name of the argument, value is the value of the argument.
    '''
    match value:
        case False:
            return
        case _ if _omit(key, value):
            return
        case True:
            yield f"--{key}"
        case str() if value in _keywords:
            yield f"--{key}={value}"
        case _:
            raise ValueError(f'{key} must be one of {_keywords} or True or False')

def arg2s(*,
          _map: dict[str, str] = {},
          _omit: Callable[[Any], Optional[str]] = lambda v: str(v or ''),
          _explicit_true: bool = False,
          _explicit_false: bool = False,
          **kwargs) -> Generator[str, None, None]:
    '''
    Return a generator of arguments of the form "--name", "value" from the given
    keyword arguments.

    If value is falsey, the argument is not included. If this is a
    problem, use arg1s instead.

    :param _map: is a dictionary mapping argument names to flag names.
    '''
    l_args = ((f'{mkflg(k, _map)}', mkstr(v))
         for k, v in kwargs.items()
         if v)
    return (item for sublist in l_args for item in sublist if item)
