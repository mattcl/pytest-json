# -*- coding: utf-8 -*-

import platform
import pytest

from pytest_json.report import JSONReport


def pytest_addoption(parser):
    group = parser.getgroup('terminal reporting')
    group.addoption(
        '--json',
        action='store',
        dest='json_path',
        default=None,
        help='where to store the JSON report'
    )
    group.addoption(
        '--jsonapi',
        action='store_true',
        dest='jsonapi',
        default=False,
        help='make the report conform to jsonapi'
    )
    parser.addini('json_report', 'where to store the JSON report')
    parser.addini('jsonapi',
                  'if present (any value), export JSON report as jsonapi',
                  default=False)


# pytest-html uses _environment already, don't conflict with it
@pytest.fixture(scope='session', autouse=True)
def json_environment(request):
    """Provide environment details for JSON report"""
    request.config._json_environment.extend([
        ('Python', platform.python_version()),
        ('Platform', platform.platform())])


def _json_path(config):
    if config.option.json_path:
        return config.option.json_path

    if config.getini('json_report'):
        return config.getini('json_report')

    return None


@pytest.fixture
def json_report_path(request):
    return _json_path(request.config)


def pytest_configure(config):
    config._json_environment = []

    json_path = _json_path(config)

    if json_path and not hasattr(config, 'slaveinput'):
        jsonapi = config.option.jsonapi or config.getini('json_report')
        config._json = JSONReport(json_path, jsonapi)
        config.pluginmanager.register(config._json)

    if hasattr(config, 'slaveoutput'):
        config.slaveoutput['json_environment'] = config._json_environment


@pytest.mark.optionalhook
def pytest_testnodedown(node):
    # deal with xdist
    if hasattr(node, 'slaveoutput'):
        node.config._json_environment = node.slaveoutput['json_environment']


def pytest_unconfigure(config):
    if hasattr(config, '_json'):
        json = config._json
        del config._json
        config.pluginmanager.unregister(json)
