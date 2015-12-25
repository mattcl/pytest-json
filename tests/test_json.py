# -*- coding: utf-8 -*-


def test_json_path_fixture(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        import pytest

        def test_sth(json_path):
            print('goodbye')
            assert json_path == "herpaderp.json"

        def test_foo(json_path):
            print('hello')
            assert 1 == 2

        @pytest.mark.xfail(reason='testing')
        def test_bar(json_path):
            print('you say')
            assert 1 == 2
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--json=herpaderp.json',
        '-v'
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_sth PASSED',
    ])

    with open('herpaderp.json', 'r') as f:
        assert f.read() == ''

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*--json=JSON_PATH*Where to store the JSON report',
    ])


# def test_json_path_ini_setting(testdir):
#     testdir.makeini("""
#         [pytest]
#         json_path = foo.json
#     """)

#     testdir.makepyfile("""
#         import pytest

#         @pytest.fixture
#         def json_path(request):
#             return request.config.getini('json_path')

#         def test_hello_world(json_path):
#             assert json_path == 'foo.json'
#     """)

#     result = testdir.runpytest('-v')

#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         '*::test_hello_world PASSED',
#     ])

#     # make sure that that we get a '0' exit code for the testsuite
#     assert result.ret == 0
