from __future__ import absolute_import
from __future__ import unicode_literals

import os

import pytest
from testing import pty
from testing.assertions import assert_svstat
from testing.subprocess import assert_command
from testing.subprocess import ctrl_c

from pgctl.daemontools import SvStat
from pgctl.subprocess import check_call
from pgctl.subprocess import PIPE
from pgctl.subprocess import Popen

pytestmark = pytest.mark.usefixtures('in_example_dir')
greeter_service = pytest.mark.parametrize('service_name', ['greeter'])
slow_startup_service = pytest.mark.parametrize('service_name', ['slow-startup'])


def read_line(fd):
    # read one-byte-at-a-time to avoid deadlocking by reading too much
    from os import read
    line = ''
    byte = None
    while byte not in ('\n', ''):
        byte = read(fd, 1).decode('utf-8')
        line += byte
    return line


@greeter_service
def assert_works_interactively():
    read, write = os.openpty()
    pty.normalize_newlines(read)
    # setsid: this simulates the shell's job-control behavior
    proc = Popen(('setsid', 'pgctl-2015', 'debug', 'greeter'), stdin=PIPE, stdout=write)
    os.close(write)

    try:
        assert read_line(read) == 'What is your name?\n'
        proc.stdin.write(b'Buck\n')
        proc.stdin.flush()
        assert read_line(read) == 'Hello, Buck.\n'
    finally:
        ctrl_c(proc)


@greeter_service
def it_works_with_nothing_running():
    assert_svstat('playground/greeter', state=SvStat.UNSUPERVISED)
    assert_works_interactively()


@greeter_service
def it_fails_with_multiple_services():
    assert_command(
        ('pgctl-2015', 'debug', 'abc', 'def'),
        '',
        '[pgctl] ERROR: Must debug exactly one service, not: abc, def\n',
        1,
    )


@greeter_service
def it_first_stops_the_background_service_if_running():
    check_call(('pgctl-2015', 'start', 'greeter'))
    assert_svstat('playground/greeter', state='running')

    assert_works_interactively()


@slow_startup_service
def it_disables_polling_heartbeat():
    from mock import patch
    with patch.dict(os.environ, [('PGCTL_TIMEOUT', '5')]):
        proc = Popen(('pgctl-2015', 'debug', 'slow-startup'), stdin=open(os.devnull), stdout=PIPE, stderr=PIPE)

    from testing.assertions import wait_for
    wait_for(lambda: assert_svstat('playground/slow-startup', state='up'))

    check_call(('pgctl-2015', 'stop'))
    stdout, stderr = proc.communicate()
    stdout, stderr = stdout.decode('UTF-8'), stderr.decode('UTF-8')

    assert stderr == '''\
[pgctl] Stopping: slow-startup
[pgctl] Stopped: slow-startup
pgctl-poll-ready: service's ready check succeeded
pgctl-poll-ready: heartbeat is disabled during debug -- quitting
'''
    assert stdout == ''
    assert proc.returncode == 0
