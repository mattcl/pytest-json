# -*- coding: utf-8 -*-
import json
import pytest
import sys
import os

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

    return [
        {
            "outcome": "skipped",
            "name": "test_report.py::test_skipped",
            "teardown": {
                "outcome": "passed",
                "name": "teardown"
            },
            "setup": {
                "longrepr": skipped_longrepr,
                "outcome": "skipped",
                "name": "setup"
            }
        },
        {
            "outcome": "failed",
            "call": {
                "longrepr": "setup_teardown_fixture = None\n\n    def test_fail_with_fixture(setup_teardown_fixture):\n        print('call str 2')\n>       assert 1 == 2\nE       assert 1 == 2\n\ntest_report.py:28: AssertionError",
                "outcome": "failed",
                "name": "call",
                "stdout": "call str 2\n"
            },
            "teardown": {
                "outcome": "passed",
                "name": "teardown",
                "stdout": "tearing down\n"
            },
            "name": "test_report.py::test_fail_with_fixture",
            "setup": {
                "stdout": "setting up\n",
                "outcome": "passed",
                "name": "setup"
            }
        },
        {
            "outcome": "error",
            "name": "test_report.py::test_fail_during_setup",
            "teardown": {
                "outcome": "passed",
                "name": "teardown"
            },
            "setup": {
                "longrepr": "request = <SubRequest 'fail_setup_fixture' for <Function 'test_fail_during_setup'>>\n\n    @pytest.fixture\n    def fail_setup_fixture(request):\n>       assert 1 == 3\nE       assert 1 == 3\n\ntest_report.py:13: AssertionError",
                "outcome": "error",
                "name": "setup"
            }
        },
        {
            "outcome": "xfailed",
            "call": {
                "outcome": "xfailed",
                "name": "call",
                "longrepr": "@pytest.mark.xfail(reason='testing xfail')\n    def test_xfailed():\n        print('I am xfailed')\n>       assert 1 == 2\nE       assert 1 == 2\n\ntest_report.py:33: AssertionError",
                "xfail_reason": "testing xfail",
                "stdout": "I am xfailed\n"
            },
            "teardown": {
                "outcome": "passed",
                "name": "teardown"
            },
            "name": "test_report.py::test_xfailed",
            "setup": {
                "outcome": "passed",
                "name": "setup"
            }
        },
        {
            "outcome": "xpassed",
            "call": {
                "xfail_reason": "testing xfail",
                "outcome": "xpassed",
                "name": "call",
                "stdout": "I am xfailed but passing\n"
            },
            "teardown": {
                "outcome": "passed",
                "name": "teardown"
            },
            "name": "test_report.py::test_xfailed_but_passing",
            "setup": {
                "outcome": "passed",
                "name": "setup"
            }
        },
        {
            "outcome": "error",
            "call": {
                "outcome": "passed",
                "name": "call",
                "stdout": "I will fail during teardown\n"
            },
            "teardown": {
                "longrepr": "def fn():\n>       assert 1 == 3\nE       assert 1 == 3\n\ntest_report.py:18: AssertionError",
                "outcome": "error",
                "name": "teardown"
            },
            "name": "test_report.py::test_fail_during_teardown",
            "setup": {
                "outcome": "passed",
                "name": "setup"
            }
        },
        {
            "outcome": "passed",
            "call": {
                "outcome": "passed",
                "name": "call",
                "stdout": "call str\n"
            },
            "teardown": {
                "outcome": "passed",
                "name": "teardown"
            },
            "name": "test_report.py::test_basic",
            "setup": {
                "outcome": "passed",
                "name": "setup"
            }
        }
    ]


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

        def test_basic(json_report_path):
            print('call str')
            assert json_report_path == "herpaderp.json"

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

    report = report['report']

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

    tests = {}
    for test in report['tests']:
        tests[test['name']] = test

    for expected in expected_data:
        test_name = expected['name']

        assert test_name in tests

        test = tests[test_name]
        assert test['outcome'] == expected['outcome']

        for stage in ['setup', 'teardown', 'call']:
            if stage in expected:
                for key, value in expected[stage].items():
                    assert test[stage][key] == value


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

    report = report['report']

    assert len(report['tests']) == 1

    foo_data = report['tests'][0]
    assert foo_data['call']['metadata'] == {'foo': 'bar'}
    assert foo_data['setup']['metadata'] == {'hoof': 'doof'}
    assert foo_data['teardown']['metadata'] == {'herp': 'derp'}


# this is a pretty crappy test for now
def test_jsonapi(testdir):
    testdir.makepyfile("""
        def test_foo():
            print('I am foo')
            assert 1 == 1

        def test_bar():
            print('I am bar')
            assert 2 == 2
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--json=herpaderp.json',
        '--jsonapi',
        '-v'
    )

    with open('herpaderp.json', 'r') as f:
        report = json.load(f)

    assert len(report['included']) == 2
    assert len(report['data'][0]['relationships']['tests']['data']) == 2

    assert result.ret == 0


def test_ini(testdir):
    testdir.makeini("""
        [pytest]
        json_report = foo.json
    """)

    testdir.makepyfile("""
        def test_foo(json_report_path):
            assert json_report_path == 'foo.json'
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '-v'
    )

    assert os.path.exists('foo.json')
    assert result.ret == 0


def test_option_overrides_ini(testdir):
    testdir.makeini("""
        [pytest]
        json_report = foo.json
    """)

    testdir.makepyfile("""
        def test_foo(json_report_path):
            assert json_report_path == 'bar.json'
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--json=bar.json',
        '-v'
    )

    assert os.path.exists('bar.json')
    assert result.ret == 0


def test_no_json_ok(testdir):
    testdir.makepyfile("""
        def test_foo():
            assert 1 == 1
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '-v'
    )

    assert result.ret == 0


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*--json=JSON_PATH*where to store the JSON report',
        '*--jsonapi*make the report conform to jsonapi',
        '*json_report (string)*where to store the JSON report',
    ])
