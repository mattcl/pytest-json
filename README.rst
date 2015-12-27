This readme is a work in progress

pytest-json
===================================

.. image:: https://travis-ci.org/mattcl/pytest-json.svg?branch=master
    :target: https://travis-ci.org/mattcl/pytest-json
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/mattcl/pytest-json?branch=master
    :target: https://ci.appveyor.com/project/mattcl/pytest-json/branch/master
    :alt: See Build Status on AppVeyor

pytest-json is a plugin for `py.test <http://pytest.org>`_ that generates JSON
reports for test results

----

This `Pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.


Features
--------

* TODO


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

.. code-block:: bash

  $ py.test --json=report.json


Adding to environment
---------------------

You can modify ``request.config._json_environment`` in a fixture

.. code-block:: python

  @pytest.fixture(scope='session', autouse=True):
  def extra_json_environment(request):
      request.config._json_environment.append(('herp', 'derp'))


Compatibility with pytest-html
------------------------------

To avoid issues with pytest-html, pytest-json uses
``request.config._json_environment`` instead of ``request.config._environment``

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
