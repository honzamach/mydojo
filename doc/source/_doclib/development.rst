.. _section-development:

Development
================================================================================

This is the documentation for developer(s) of the project itself.


Key information
--------------------------------------------------------------------------------

* `Project issue tracking system <https://github.com/honzamach/mydojo>`__
* `Source code repository <https://github.com/honzamach/mydojo.git>`__
* `MyDojo: official website <https://jan-mach.cz>`__


General guidelines
--------------------------------------------------------------------------------

* Let `PEP 20 <https://www.python.org/dev/peps/pep-0020/>`__ be the guide for your mind.
* Let `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`__ be the guide for your hand.
* Let you and `PEP 257 <https://www.python.org/dev/peps/pep-0257/>`__ and `PEP 287 <https://www.python.org/dev/peps/pep-0287/>`__ be the guide for others.

* Use `Sphinx-doc <http://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`__ format to document the code.
* Pull and merge often.
* Use *devel* branch for small updates and bugfixes.
* For bigger features fork *devel*, merge after accepting, delete branch.
* Use *master* branch only for production level and stable code.


Versioning
--------------------------------------------------------------------------------

This project uses the `semantic versioning <https://semver.org/>`__. Version number
must be changed in following files:

* ``mydojo/__init__.py``


Tagging
--------------------------------------------------------------------------------

Each major and minor version release must be tagged within the repository. Please
use only annotated or signed tags and provide short comment for the release. Before
tagging please view existing tags so that you can attempt to maintain the style of
the tag messages.

.. code-block:: shell

	# List all existing tags
	git tag -l -n999

	# Create new annotated tag and provide message
	git tag -a v1.0.0

	# Push tags to remote server
	git push origin v1.0.0

	# Number of commits between last two versions:
	git rev-list --count v1.0.0..v0.0.1

	# Total changes between last two versions:
	git log --numstat --pretty="%H" v1.0.0..v0.0.1 | awk 'NF==3 {plus+=$1; minus+=$2} END {printf("+%d, -%d\n", plus, minus)}'


Preparing environment
--------------------------------------------------------------------------------

Please execute the following command to install project locally in editable mode
including all development dependencies:

.. code-block:: shell

	make install-dev


Development essentials
--------------------------------------------------------------------------------

There is a project master *Makefile* in the root of the project repository which
can perform various usefull or essential development tasks. You can get the full
list of all available make commands/targets by executing one of the following
commands::

	make
	make help


Producing database migrations
````````````````````````````````````````````````````````````````````````````````

To create new database migration update database model in :py:mod:`mydojo.db` as
necessary and then execute following commands::

	# Produce new migration version:
	mydojo-cli db migrate -m "Change description: some additional description"

	# Review and possibly update the newly generated migration in directory
	# ``mydojo/migrations/versions/[something].py

	# Apply the migration locally:
	mydojo-cli db upgrade

	# Optionally verify the current state of database schema:
	mydojo-cli db history
	mydojo-cli db current
	mydojo-cli db show


Checking code with Pyflakes
````````````````````````````````````````````````````````````````````````````````

You may check the whole codebase with `Pyflakes <https://github.com/PyCQA/pyflakes>`__
tool by executing following command:

.. code-block:: shell

	make pyflakes

Or you may check just the single file by executing following command:

.. code-block:: shell

	cd lib
	pyflakes path/to/module.py

Make sure, that the `pyflakes <https://pypi.org/project/pyflakes/>`__ library is
already installed on your system. You may install it by executing following command:

.. code-block:: shell

	pip3 install pyflakes


Checking code with Pylint
````````````````````````````````````````````````````````````````````````````````

You may check the whole codebase with `Pylint <https://pylint.readthedocs.io/en/latest/>`__
tool by executing following command:

.. code-block:: shell

	make pylint

Or you may check just the single file by executing following command:

.. code-block:: shell

	cd lib
	pylint --rcfile=../.pylintrc-lib path/to/module.py

Make sure, that the `pylint <https://pypi.org/project/pylint/>`__ library is already
installed on your system. You may install it by executing following command:

.. code-block:: shell

	pip3 install pylint


Running unit tests
````````````````````````````````````````````````````````````````````````````````

You may run prepared unit tests on the whole codebase by executing the following
command:

.. code-block:: shell

	make test

Make sure, that the `nose <https://pypi.org/project/nose/>`__ library is already
installed on your system. You may install it by executing following command:

.. code-block:: shell

	pip3 install nose


Documentation
````````````````````````````````````````````````````````````````````````````````

Project documentation is generated using the `Sphinx-doc <http://www.sphinx-doc.org/en/stable/contents.html>`__
tool into various formats. Please use `RST <http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`__
markup features where appropriate to increase readability and cross-reference to
related content. It should however still be possible to view the documentation of
all Python modules in *Pythonic* way via `pydoc3 <https://docs.python.org/3/library/pydoc.html>`__
and the result should still be more or less readable. Please test it immediately with:

.. code-block:: shell

	pydoc3 ./path/to/module.py

You may generate and review the documentation locally by executing the following
command:

.. code-block:: shell

	make docs

Make sure, that the `Sphinx <https://pypi.org/project/sphinx/>`__ and
`sphinx-rtd-theme <https://pypi.org/project/sphinx-rtd-theme/>`__ libraries are
already installed on your system. You may install them by executing following
commands:

.. code-block:: shell

	pip3 install sphinx
	pip3 install sphinx_rtd_theme

Documentation will be generated into ``doc/build/html/manual.html``.


Important resources
````````````````````````````````````````````````````````````````````````````````

* `pyflakes <https://github.com/PyCQA/pyflakes>`__
* `pylint <https://pylint.readthedocs.io/en/latest/>`__
* `nosetests <http://nose.readthedocs.io/en/latest/>`__
* `pydoc3 <https://docs.python.org/3/library/pydoc.html>`__
* `Sphinx-doc <http://www.sphinx-doc.org/en/stable/contents.html>`__

  * `reStructuredText Primer <http://www.sphinx-doc.org/en/stable/rest.html>`__
  * `Sphinx markup constructs <http://www.sphinx-doc.org/en/stable/markup/index.html>`__
  * `The Python domain <http://www.sphinx-doc.org/en/stable/domains.html#the-python-domain>`__
  * `Documenting functions and methods <http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists>`__
