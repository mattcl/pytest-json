the json schema is highly in flux at the moment

pytest-json
===================================

.. image:: https://travis-ci.org/mattcl/pytest-json.svg?branch=master
    :target: https://travis-ci.org/mattcl/pytest-json
    :alt: See Build Status on Travis CI

pytest-json is a plugin for `py.test <http://pytest.org>`_ that generates JSON
reports for test results

----

This `Pytest`_ plugin was generated with `Cookiecutter`_ along with
`@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.


Requirements
------------

- Python 2.7, 3.3, 3.4, 3.5
- py.test 2.7 or newer


Installation
------------

You can install "pytest-json" via `pip`_ from `PyPI`_::

  $ pip install pytest-json


Usage
-----

.. code-block::

  $ py.test --json=report.json

or you can set the report path in an ini file::

  [pytest]
  json_report = report.json

The command-line option will override the ini file

There is an optional flag to normalize the generated report to
`jsonapi <http://jsonapi.org>`_. This is intended for (easier) consumption by
ember-data and others::

  $ py.test --json=report.json --jsonapi


Adding to environment
---------------------

You can modify ``request.config._json_environment`` in a fixture

.. code-block:: python

  @pytest.fixture(scope='session', autouse=True):
  def extra_json_environment(request):
      request.config._json_environment.append(('herp', 'derp'))


Adding metadata per test stage
------------------------------

.. code-block:: python

  # conftest.py
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


Compatibility with pytest-html
------------------------------

To avoid issues with pytest-html, pytest-json uses
``request.config._json_environment`` instead of ``request.config._environment``

Additionally, pytest-json ignores the ``extra`` field on reports.


Example json
------------

A formatted example of the output can be found in example.json

The actual output is not formatted, but this was passed through jq for
readability.

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-json" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/mattcl/pytest-json/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.org/en/latest/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi
