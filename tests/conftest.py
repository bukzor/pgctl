# -*- coding: utf-8 -*-
# pylint:disable=redefined-outer-name,unused-argument
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import shutil

from py._path.local import LocalPath as Path
from pytest import yield_fixture as fixture

TOP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from pgctl.cli import PgctlApp


@fixture
def in_example_dir(tmpdir, homedir, service_name):
    os.environ['HOME'] = homedir.strpath
    os.environ.pop('XDG_RUNTIME_DIR', None)

    template_dir = os.path.join(TOP, 'tests/examples', service_name)
    tmpdir = tmpdir.join(service_name)
    shutil.copytree(template_dir, tmpdir.strpath)

    with tmpdir.as_cwd():
        try:
            yield tmpdir
        finally:
            #  pytest does a chdir before calling cleanup handlers
            with tmpdir.as_cwd():
                PgctlApp().stop()


def debug():
    from pgctl.flock import flock
    with flock('debug.lock'):
        import sys
        tty = '/dev/pts/85'

        #os.close(0)
        mytty = open(tty)
        sys.stdin = sys.__stdin__ = mytty
        fd = mytty.fileno()
        os.dup2(fd, 0)

        #os.close(1)
        mytty = open(tty, 'w')
        sys.stdout = sys.__stdout__ = mytty
        fd = mytty.fileno()
        os.dup2(fd, 1)

        #os.close(2)
        mytty = open(tty, 'w')
        sys.stderr = sys.__stderr__ = mytty
        fd = mytty.fileno()
        os.dup2(fd, 2)

        import pudb
        pudb.set_trace()


def show_time(msg, outfile, tmpdir):
    import sys
    from datetime import datetime
    import coverage.control
    outfile.write(
        '''

%s: %s
sys.gettrace: %s
coverage.process_startup.done: %s
argv: %s
pid: %s
tmpdir: %s

'''
        % (
            msg,
            datetime.now().strftime('%F %T.%f'),
            sys.gettrace(),
            coverage.control.process_startup.done,
            sys.argv,
            os.getpid(),
            tmpdir,
        )
    )


@fixture(autouse=True, scope='session')
def show_atexit(request):
    tty = open('/dev/tty', 'w')
    import atexit
    atexit.register(lambda: show_time('atexit', tty, request.config.option.basetemp))
    yield


@fixture
def scratch_dir(pghome_dir, service_name, in_example_dir):
    yield pghome_dir.join(Path().join('playground', service_name).relto(str('/')))


@fixture
def pghome_dir(homedir):
    yield homedir.join('.run', 'pgctl')


@fixture
def homedir(tmpdir):
    yield tmpdir.join('home')


@fixture
def service_name():
    # this fixture will be overridden by some tests
    yield 'sleep'


@fixture(autouse=True)
def disinherit_pytest_pipe():
    """
    pytest creates some weird pipe on fd3 when running under xdist
    this prevents tests from ending due to subprocesses

    Solution: disinherit the pipe.
    """
    from pgctl.functions import set_non_inheritable
    try:
        set_non_inheritable(3)
    except IOError as error:  # this only happens under single-process pytest  :pragma:nocover:
        if error.errno == 9:  # no such fd
            pass
        else:
            raise
    yield


@fixture(autouse=True)
def wait4(tmpdir):
    """wait for all subprocesses to finish."""
    lock = tmpdir.join('pytest-subprocesses.lock')
    try:
        from pgctl.flock import flock
        with flock(lock.strpath):
            yield
    finally:
        from pgctl.fuser import fuser
        from pgctl.functions import ps
        fusers = True
        i = 0
        while fusers and i < 10:
            fusers = tuple(fuser(lock.strpath))
            i += 1  # we only hit this when tests are broken. pragma: no cover
        fusers = ps(fusers)
        if fusers:
            raise AssertionError("there's a subprocess that's still running:\n%s" % ps(fusers))
