#!/usr/bin/env python

from typing import Optional
from pathlib import Path
from subprocess import run
import os
from gitgo.log import log
from gitgo.lowlevel.cmdargs import CmdArg, CmdResult

last_cwd: Optional[Path] = None
def track_cwd():
    global last_cwd
    cwd = Path.cwd()
    if cwd != last_cwd:
        log.info(f"> cd {cwd}")
        last_cwd = cwd

def runner(cmd: str):
    '''
    Produce a standard command runner
    '''
    def do_run(*args: CmdArg,
            check: bool = True,
            boolean_return: bool = False,
            capture_output=True,
            input: Optional[str] = None,
            text: bool = True,
            **kwargs) -> CmdResult:
        '''
        Run command with the given arguments.
        Output to stderr is logged at the error level.
        :param check: If True, raise an exception if the command fails
            default: True
        :param boolean_return: If True, return a tuple of (stdout, True/False)
            indicating whether the command succeeded. Return codes other than
            0 and 1 are still treated as errors.
            default: False
        :param capture_output: If True, capture stdout and stderr.
            default: True
        '''
        xargs = [str(a) for a in args]
        if boolean_return:
            check = False
        log.debug(f"> {cmd}{xargs}")
        p = run([cmd, *xargs],
                text=text,
                input=input,
                capture_output=capture_output,
                **kwargs)
        p_err = p.stderr
        if p_err:
            log.warn('%s', p_err)
        if check and p.returncode != 0:
            log.error(f'''{cmd}{xargs} returned {p.returncode}
cwd={os.getcwd()}
stdout={p.stdout}
stdout={p.stdout}''')
            raise ValueError(f"{cmd}{xargs} returned {p.returncode}")
        if boolean_return:
            if p.returncode and p.returncode != 1:
                raise ValueError(f"{cmd}{xargs} returned {p.returncode}")
            return CmdResult(p.stdout, p.stderr,  p.returncode == 0)
        return CmdResult(p.stdout, p.stderr, p.returncode)
    return do_run

ssh = runner('ssh')
