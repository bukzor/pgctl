Bug Log
=======

This is a log of bugs we've run into, and how they were solved.
This proves helpful when we run into an old bug again,
or if we need to remember why we added some particular workaround.


Missing Coverage (2015-10-22)
-----------------------------
We're seeing coverage drop out for no apparent reason, but only under cpu-constrained circumstances (yelp-jenkins, circleci).

I've found some clues:

    * only lines run *directly* by the xdist workers goes missing; all subprocess coverage is reliable.
    * the xdist worker does write out its coverage file on time, it's just (mostly) empty.
    * TODO: does this reproduce using coverage<4.0 ?


### Circle CI debugging

To grab files from a circleCI run: (for example)

    rsync -Pav  -e 'ssh -p 64785' ubuntu@54.146.184.147:pgctl/coverage.bak.2015-10-24_18:28:36.937047774 .

### Bad Data

This is an example of a bad data file. This is from a process that ran several unit tests, so it should have covered
*something*.

    $ python -m coverage.data coverage.bak.2015-10-24_19\:30\:13.528090258/.coverage.box821.27569.514441 
    --- coverage.bak.2015-10-24_19:30:13.528090258/.coverage.box821.27569.514441 ------------------------------
    {
        "arcs": {
            "/home/ubuntu/pgctl/tests/conftest.py": [
                [-1, 91],
                [80, 81],
                [69, 74],
                [77, 78],
                [68, 69],
                [79, 80],
                [-1, 66],
                [74, 76],
                [76, 77],
                [66, 67],
                [81, 82],
                [91, -91],
                [82, -65],
                [78, 79],
                [67, 68]
            ],
            "/home/ubuntu/pgctl/tests/spec/__init__.py": [],
            "/home/ubuntu/pgctl/tests/spec/cli.py": [],
            "/home/ubuntu/pgctl/tests/spec/config.py": [],
            "/home/ubuntu/pgctl/tests/spec/configsearch.py": [],
            "/home/ubuntu/pgctl/tests/spec/debug.py": [],
            "/home/ubuntu/pgctl/tests/spec/dirty_tests.py": [],
            "/home/ubuntu/pgctl/tests/spec/examples.py": [],
            "/home/ubuntu/pgctl/tests/spec/fuser.py": [],
            "/home/ubuntu/pgctl/tests/spec/parallel.py": [],
            "/home/ubuntu/pgctl/tests/spec/slow_startup.py": [],
            "/home/ubuntu/pgctl/tests/testing/__init__.py": [],
            "/home/ubuntu/pgctl/tests/testing/assertions.py": [],
            "/home/ubuntu/pgctl/tests/testing/assertions_test.py": [],
            "/home/ubuntu/pgctl/tests/testing/get_modulefile.py": [],
            "/home/ubuntu/pgctl/tests/testing/install_coverage_pth.py": [],
            "/home/ubuntu/pgctl/tests/testing/norm.py": [],
            "/home/ubuntu/pgctl/tests/testing/pty.py": [],
            "/home/ubuntu/pgctl/tests/testing/subprocess.py": [],
            "/home/ubuntu/pgctl/tests/testing/wait_for_files.py": [],
            "/home/ubuntu/pgctl/tests/unit/__init__.py": [],
            "/home/ubuntu/pgctl/tests/unit/config.py": [],
            "/home/ubuntu/pgctl/tests/unit/configsearch.py": [],
            "/home/ubuntu/pgctl/tests/unit/flock.py": [],
            "/home/ubuntu/pgctl/tests/unit/functions.py": [],
            "/home/ubuntu/pgctl/tests/unit/poll_ready_test.py": [],
            "/home/ubuntu/pgctl/tests/unit/service.py": []
        }
    }


This is the data I have about that process:


    [gw2] PASSED ../../../tests/spec/examples.py::DescribePgctlLog::it_shows_stdout_and_stderr 
    [gw2] FAILED ../../../tests/spec/examples.py::DescribePgctlLog::it_logs_continuously_when_run_interactively 
    [gw2] ERROR ../../../tests/spec/examples.py::DescribePgctlLog::it_logs_continuously_when_run_interactively 
    [gw2] PASSED ../../../tests/spec/examples.py::DescribePgctlLog::it_is_line_buffered 
    [gw2] PASSED ../../../tests/spec/examples.py::DescribePgdirMissing::it_can_still_show_config 
    [gw2] PASSED ../../../tests/spec/examples.py::DescribePgdirMissing::it_can_still_show_help 
    <snip>
    [gw2] PASSED ../../../tests/unit/poll_ready_test.py::DescribeGetVal::it_loads_default_var 
    [gw2] PASSED ../../../tests/unit/service.py::test_str_and_repr 
    [gw2] PASSED ../lib/python2.7/site-packages/pgctl/daemontools.py::pgctl.daemontools.svstat_parse 

    atexit:2015-10-24 19:30:07.295429 sys.gettrace:<coverage.CTracer object at 0x7f5151678538> coverage.process_startup.done:True argv:['-c'] pid:27569 tmpdir:/tmp/pytest-ubuntu/pytest-1/popen-gw2

    (coverage was combined just after 2015-10-24 19:30:13.526772329)


This was the missing coverage. It correlates directly to the test run by "gw2".

    ++ coverage report --rcfile=/home/ubuntu/pgctl/.coveragerc --fail-under 100
    Name                                                                               Stmts   Miss Branch BrPart  Cover   Missing
    ------------------------------------------------------------------------------------------------------------------------------
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/__init__.py           3      0      0      0   100%   
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/cli.py              229      0     38      0   100%   
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/config.py           105      1     40      2    98%   82, 81->82, 97->100
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/configsearch.py      53      0     25      0   100%   
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/daemontools.py       89      5     28      3    91%   137, 145, 164-167, 136->137, 138->145, 162->164
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/debug.py             13      0      0      0   100%   
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/errors.py            10      0      0      0   100%   
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/flock.py             29      0      0      0   100%   
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/functions.py         53      1     16      2    96%   52, 48->52, 56->59
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/fuser.py             47      0     10      0   100%   
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/poll_ready.py        57      0     18      0   100%   
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/service.py          130      1     20      0    99%   47
    /home/ubuntu/pgctl/.tox/python/lib/python2.7/site-packages/pgctl/timestamp.py         26      0      8      0   100%   
    /home/ubuntu/pgctl/tests/conftest.py                                                  76     20      4      0    75%   37-62, 97, 102
    /home/ubuntu/pgctl/tests/spec/__init__.py                                              0      0      0      0   100%   
    /home/ubuntu/pgctl/tests/spec/cli.py                                                  17      5      0      0    71%   30-59
    /home/ubuntu/pgctl/tests/spec/config.py                                               34      0      0      0   100%   
    /home/ubuntu/pgctl/tests/spec/configsearch.py                                         18      0      0      0   100%   
    /home/ubuntu/pgctl/tests/spec/debug.py                                                53      5      4      1    89%   82-92, 80->82
    /home/ubuntu/pgctl/tests/spec/dirty_tests.py                                          72     15      6      0    81%   176, 180-182, 185-187, 204-214
    /home/ubuntu/pgctl/tests/spec/examples.py                                            185     64     22      1    66%   27, 30, 42-60, 77-132, 168, 171-173, 180, 183-190, 196, 322-323, 333-334, 347-348, 474-493, 501-502, 134->-134
    /home/ubuntu/pgctl/tests/spec/fuser.py                                                20      0      0      0   100%   
    /home/ubuntu/pgctl/tests/spec/parallel.py                                             25      0      0      0   100%   
    /home/ubuntu/pgctl/tests/spec/slow_startup.py                                         42     20      0      0    52%   57-66, 71-84, 103-107
    /home/ubuntu/pgctl/tests/testing/__init__.py                                           0      0      0      0   100%   
    /home/ubuntu/pgctl/tests/testing/assertions.py                                        17      2      2      0    89%   20-21
    /home/ubuntu/pgctl/tests/testing/assertions_test.py                                   18     10      4      0    36%   13, 16-17, 20-28
    /home/ubuntu/pgctl/tests/testing/get_modulefile.py                                    10      0      0      0   100%   
    /home/ubuntu/pgctl/tests/testing/install_coverage_pth.py                               8      0      0      0   100%   
    /home/ubuntu/pgctl/tests/testing/norm.py                                              11      0      2      0   100%   
    /home/ubuntu/pgctl/tests/testing/pty.py                                                7      0      0      0   100%   
    /home/ubuntu/pgctl/tests/testing/subprocess.py                                        39      0      4      0   100%   
    /home/ubuntu/pgctl/tests/testing/wait_for_files.py                                    28      0      6      0   100%   
    /home/ubuntu/pgctl/tests/unit/__init__.py                                              0      0      0      0   100%   
    /home/ubuntu/pgctl/tests/unit/config.py                                              106     44      0      0    58%   94-100, 103-104, 107-111, 114-117, 123-124, 127-128, 131-133, 139, 145, 153, 181-182, 220-225, 228-236, 249-253
    /home/ubuntu/pgctl/tests/unit/configsearch.py                                         43     21      4      0    51%   19-20, 23-24, 27-28, 35-37, 46-49, 55-62
    /home/ubuntu/pgctl/tests/unit/flock.py                                                50     13      0      0    74%   33-36, 39-43, 53-61
    /home/ubuntu/pgctl/tests/unit/functions.py                                            40      8      0      0    80%   24-25, 51-52, 58-60, 77
    /home/ubuntu/pgctl/tests/unit/poll_ready_test.py                                      35      9      0      0    74%   22-27, 48-50
    /home/ubuntu/pgctl/tests/unit/service.py                                               8      2      0      0    75%   12-13
    ------------------------------------------------------------------------------------------------------------------------------
    TOTAL                                                                               1806    246    261      9    87%   
