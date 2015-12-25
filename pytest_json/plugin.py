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
        help='Where to store the JSON report'
    )


# pytest-html uses _environment already, don't conflict with it
@pytest.fixture(scope='session', autouse=True)
def json_environment(request):
    """Provide environment details for JSON report"""
    request.config._json_environment.extend([
        ('Python', platform.python_version()),
        ('Platform', platform.platform())])


@pytest.fixture
def json_path(request):
    return request.config.option.json_path


def pytest_configure(config):
    config._json_environment = []
    json_path = config.option.json_path

    if json_path and not hasattr(config, 'slaveinput'):
        config._json = JSONReport(json_path)
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
