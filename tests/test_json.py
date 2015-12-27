# -*- coding: utf-8 -*-
import json
import pytest
import sys

PY3 = sys.version_info[0] == 3


# note that we don't have duration in here, but this is because we can't
# assert on something that will change test to test (and I don't know how
# to mock time for the underlying pytest call)
@pytest.fixture
def expected_data():

    # FIXME:- MCL - 2015-12-26
    # I'm not sure why json loads in putting the 'u' in the middle of a string,
    # but I need to get the other stuff working first. Revisit.
    if not PY3:
        skipped_longrepr = "('test_report.py', 47, u'Skipped: testing skip')"
    else:
        skipped_longrepr = "('test_report.py', 47, 'Skipped: testing skip')"

    return {
        "test_report.py::test_xfailed_but_passing": {
            "teardown": {
                "outcome": "passed"
            },
            "setup": {
                "outcome": "passed"
            },
            "call": {
                "xfail_reason": "testing xfail",
                "Captured stdout call": "I am xfailed but passing\n",
                "outcome": "xpassed"
            }
        },
        "test_report.py::test_skipped": {
            "teardown": {
                "outcome": "passed"
            },
            "setup": {
                "longrepr": skipped_longrepr,
                "outcome": "skipped"
            }
        },
        "test_report.py::test_fail_during_setup": {
            "teardown": {
                "outcome": "passed"
            },
            "setup": {
                "longrepr": "request = <SubRequest 'fail_setup_fixture' for <Function 'test_fail_during_setup'>>\n\n    @pytest.fixture\n    def fail_setup_fixture(request):\n>       assert 1 == 3\nE       assert 1 == 3\n\ntest_report.py:13: AssertionError",
                "outcome": "error"
            }
        },
        "test_report.py::test_basic": {
            "teardown": {
                "outcome": "passed"
            },
            "setup": {
                "outcome": "passed"
            },
            "call": {
                "Captured stdout call": "call str\n",
            }
        },
        "test_report.py::test_fail_with_fixture": {
            "teardown": {
                "Captured stdout teardown": "tearing down\n",
                "outcome": "passed"
            },
            "setup": {
                "Captured stdout setup": "setting up\n",
                "outcome": "passed"
            },
            "call": {
                "longrepr": "setup_teardown_fixture = None\n\n    def test_fail_with_fixture(setup_teardown_fixture):\n        print('call str 2')\n>       assert 1 == 2\nE       assert 1 == 2\n\ntest_report.py:28: AssertionError",
                "Captured stdout call": "call str 2\n",
                "outcome": "failed"
            }
        },
        "test_report.py::test_fail_during_teardown": {
            "teardown": {
                "longrepr": "def fn():\n>       assert 1 == 3\nE       assert 1 == 3\n\ntest_report.py:18: AssertionError",
                "outcome": "error"
            },
            "setup": {
                "outcome": "passed"
            },
            "call": {
                "Captured stdout call": "I will fail during teardown\n",
                "outcome": "passed"
            }
        },
        "test_report.py::test_xfailed": {
            "teardown": {
                "outcome": "passed"
            },
            "setup": {
                "outcome": "passed"
            },
            "call": {
                "longrepr": "@pytest.mark.xfail(reason='testing xfail')\n    def test_xfailed():\n        print('I am xfailed')\n>       assert 1 == 2\nE       assert 1 == 2\n\ntest_report.py:33: AssertionError",
                "xfail_reason": "testing xfail",
                "Captured stdout call": "I am xfailed\n",
                "outcome": "xfailed"
            }
        }
    }


# so because testdir can't be session-scoped, do this all in one test
def test_report(testdir, expected_data):
    # create a temporary pytest test module
    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def setup_teardown_fixture(request):
            print('setting up')
            def fn():
                print('tearing down')

            request.addfinalizer(fn)

        @pytest.fixture
        def fail_setup_fixture(request):
            assert 1 == 3

        @pytest.fixture
        def fail_teardown_fixture(request):
            def fn():
                assert 1 == 3

            request.addfinalizer(fn)

        def test_basic(json_path):
            print('call str')
            assert json_path == "herpaderp.json"

        def test_fail_with_fixture(setup_teardown_fixture):
            print('call str 2')
            assert 1 == 2

        @pytest.mark.xfail(reason='testing xfail')
        def test_xfailed():
            print('I am xfailed')
            assert 1 == 2

        @pytest.mark.xfail(reason='testing xfail')
        def test_xfailed_but_passing():
            print('I am xfailed but passing')
            assert 1 == 1

        def test_fail_during_setup(fail_setup_fixture):
            print('I failed during setup')
            assert 1 == 1

        def test_fail_during_teardown(fail_teardown_fixture):
            print('I will fail during teardown')
            assert 1 == 1

        @pytest.mark.skipif(True, reason='testing skip')
        def test_skipped():
            assert 1 == 2
    """)

    # run pytest with the following cmd args
    testdir.runpytest(
        '--json=herpaderp.json',
        '-v'
    )

    with open('herpaderp.json', 'r') as f:
        report = json.load(f)

    # summary
    assert report['summary']['num_tests'] == 7
    assert report['summary']['xfailed'] == 1
    assert report['summary']['failed'] == 1
    assert report['summary']['passed'] == 2
    assert report['summary']['error'] == 2
    assert report['summary']['xpassed'] == 1
    assert report['summary']['skipped'] == 1

    # tests
    assert len(report['tests']) == 7
    for test, stage_data in expected_data.items():
        assert test in report['tests']

        for stage, data in stage_data.items():
            for key, value in data.items():
                assert report['tests'][test][stage][key] == value


def test_metadata(testdir):
    testdir.makeconftest("""
        import pytest

        @pytest.hookimpl(tryfirst=True, hookwrapper=True)
        def pytest_runtest_makereport(item, call):
            outcome = yield
            report = outcome.get_result()
            if report.when == 'call':
                report.metadata = {
                    'foo': 'bar'
                }
            elif report.when == 'setup':
                report.metadata = {
                    'hoof': 'doof'
                }
            elif report.when == 'teardown':
                report.metadata = {
                    'herp': 'derp'
                }
    """)

    testdir.makepyfile("""
        def test_foo():
            assert 1 == 1
    """)

    # run pytest with the following cmd args
    testdir.runpytest(
        '--json=herpaderp.json',
        '-v'
    )

    with open('herpaderp.json', 'r') as f:
        report = json.load(f)

    assert len(report['tests']) == 1

    foo_data = report['tests']['test_metadata.py::test_foo']
    assert foo_data['call']['metadata'] == {'foo': 'bar'}
    assert foo_data['setup']['metadata'] == {'hoof': 'doof'}
    assert foo_data['teardown']['metadata'] == {'herp': 'derp'}


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*--json=JSON_PATH*Where to store the JSON report',
    ])
