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


Development essentials
--------------------------------------------------------------------------------

There is a project master *Makefile* in the root of the project repository which
can perform various usefull or essential development tasks. You can get the full
list of all available make commands/targets by executing one of the following
commands::

	$ make
	$ make help


Preparing development environment
````````````````````````````````````````````````````````````````````````````````

There are several development prerequisites, that already have to be present on
your development machine. These prerequisites are not installed automatically
for you, because the installation is too complex. There prerequisites are:

* `Python 3 <https://www.python.org/>`__: Please use version similar to current stable Python3 release on current stable Debian release.
* `Pip <https://pip.pypa.io/en/stable/>`__: Python package manager, we recommend installation with `get-pip.py <https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py>`__.
* `Yarn <https://yarnpkg.com/en/>`__: NPM package manager for web interface libraries.
* `Grunt <https://gruntjs.com/>`__: JavaScript task runner for web interface development.
* `PostgreSQL 11 <https://www.postgresql.org/>`__: Relational database, please use version 11 wherever possible.

You can check for presence of all of these dependencies with this handy make target:

.. code-block:: shell

	# Check for presence of all prerequisites:
	$ make deps-prerequisites

Now please execute the following command from the root directory of the repository to
initialize correct Python virtual environment, install all requirements (including
those only for development) and finally install the project locally in editable mode:

.. code-block:: shell

	# Perform all installations:
	$ make develop

	# Activate virtual environment before any development work:
	$ . venv/bin/activate

	# Now from within the virtual environment install all required dependencies:
	(venv) $ make deps

	# Deactivate virtual environment when not needed with:
	$ deactivate


Checking code with Pyflakes
````````````````````````````````````````````````````````````````````````````````

You may check the whole codebase with `Pyflakes <https://github.com/PyCQA/pyflakes>`__
tool by executing following command:

.. code-block:: shell

	# Always make sure your virtual environment is activated:
	$ . venv/bin/activate

	# Run tests:
	(venv) $ make pyflakes

Or you may check just the single file by executing following command:

.. code-block:: shell

	# Always make sure your virtual environment is activated:
	$ . venv/bin/activate

	# Run tests:
	(venv) $ pyflakes path/to/module.py

Important resources:

* `pyflakes <https://github.com/PyCQA/pyflakes>`__


Checking code with Pylint
````````````````````````````````````````````````````````````````````````````````

You may check the whole codebase with `Pylint <https://pylint.readthedocs.io/en/latest/>`__
tool by executing following command:

.. code-block:: shell

	# Always make sure your virtual environment is activated:
	$ . venv/bin/activate

	# Run tests:
	(venv) $ make pylint

Or you may check just the single file by executing following command:

.. code-block:: shell

	# Always make sure your virtual environment is activated:
	$ . venv/bin/activate

	# Run tests:
	(venv) $ pylint --rcfile=../.pylintrc path/to/module.py

Important resources:

* `pylint <https://pylint.readthedocs.io/en/latest/>`__


Running unit tests
````````````````````````````````````````````````````````````````````````````````

You may run prepared unit tests on the whole codebase by executing the following
command:

.. code-block:: shell

	# Always make sure your virtual environment is activated:
	$ . venv/bin/activate

	# Run tests:
	(venv) $ make test

Important resources:

* `nosetests <http://nose.readthedocs.io/en/latest/>`__


Documentation
````````````````````````````````````````````````````````````````````````````````

Project documentation is generated using the `Sphinx-doc <http://www.sphinx-doc.org/en/stable/contents.html>`__
tool into various formats. Please use `RST <http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`__
markup features where appropriate to increase readability and cross-reference to
related content. It should however still be possible to view the documentation of
all Python modules in *Pythonic* way via `pydoc3 <https://docs.python.org/3/library/pydoc.html>`__
and the result should still be more or less readable. Please test it immediately with:

.. code-block:: shell

	# Always make sure your virtual environment is activated:
	$ . venv/bin/activate

	# Run tests:
	(venv) $ pydoc3 ./path/to/module.py

You may generate and review the documentation locally by executing the following
command:

.. code-block:: shell

	# Always make sure your virtual environment is activated:
	$ . venv/bin/activate

	# Run tests:
	(venv) $ make docs

Documentation will be generated into ``doc/build/html/manual.html``.

Important resources:

* `pydoc3 <https://docs.python.org/3/library/pydoc.html>`__
* `Sphinx-doc <http://www.sphinx-doc.org/en/stable/contents.html>`__

  * `reStructuredText Primer <http://www.sphinx-doc.org/en/stable/rest.html>`__
  * `Sphinx markup constructs <http://www.sphinx-doc.org/en/stable/markup/index.html>`__
  * `The Python domain <http://www.sphinx-doc.org/en/stable/domains.html#the-python-domain>`__
  * `Documenting functions and methods <http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists>`__


Producing database migrations
````````````````````````````````````````````````````````````````````````````````

To create new database migration update database model in :py:mod:`mydojo.db` as
necessary and then execute following commands::

	# Produce new migration version:
	(venv) $ mydojo-cli db migrate -m "Change description: some additional description"

	# Review and possibly update the newly generated migration in directory
	# ``mydojo/migrations/versions/[something].py

	# Apply the migration locally:
	(venv) $ mydojo-cli db upgrade

	# Optionally verify the current state of database schema:
	(venv) $ mydojo-cli db history
	(venv) $ mydojo-cli db current
	(venv) $ mydojo-cli db show

Important resources:

* `Alembic <https://alembic.sqlalchemy.org/en/latest/index.html>`__
* `Flask-Migrate <https://flask-migrate.readthedocs.io/en/latest/>`__


Versioning
--------------------------------------------------------------------------------

This project uses the `semantic versioning <https://semver.org/>`__. Version number
must be changed in following files:

* ``mydojo/__init__.py``
* ``setup.py``


Tagging
--------------------------------------------------------------------------------

Each major and minor version release must be tagged within the repository. Please
use only annotated or signed tags and provide short comment for the release. Before
tagging please view existing tags so that you can attempt to maintain the style of
the tag messages.

.. code-block:: shell

	# List all existing tags
	$ git tag -l -n999

	# Create new annotated tag and provide message
	$ git tag -a v1.0.0

	# Push tags to remote server
	$ git push origin v1.0.0

	# Number of commits between last two versions:
	$ git rev-list --count v1.0.0..v0.0.1

	# Total changes between last two versions:
	$ git log --numstat --pretty="%H" v1.0.0..v0.0.1 | awk 'NF==3 {plus+=$1; minus+=$2} END {printf("+%d, -%d\n", plus, minus)}'
