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

Of course you need to have *make* utility installed on your system, on Debian-based
system you can use following command::

	$ aptitude install make


Development prerequisites
````````````````````````````````````````````````````````````````````````````````

There are several development prerequisites, that already have to be present on
your development machine. These prerequisites are not installed automatically for
you, because the installation is too complex, too customizable or simply best to
be performed by the user himself. These prerequisites currently are:

* `Python 3 <https://www.python.org/>`__: Please use version similar to current stable Python3 release on current stable Debian release (`current <https://packages.debian.org/stretch/python3>`__).
* `Pip <https://pip.pypa.io/en/stable/>`__: Python package manager, we recommend installation with `get-pip.py <https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py>`__ to get the latest release, you may sometimes encounter weird bugs when installing newer packages with old versions of pip.
* `Yarn <https://yarnpkg.com/en/>`__: NPM package manager for web interface libraries. This package manager is responsible for managing frontend development libraries like jQuery, Bootstrap, D3 etc.
* `Grunt <https://gruntjs.com/>`__: JavaScript task runner for web interface development. It is responsible for taking care of frontend related tasks like JavaScript and CSS minification
* `PostgreSQL 11 <https://www.postgresql.org/>`__: Relational database, used for persistent data storage. Please use version 11 wherever possible.

You can check for presence of all of these dependencies with this handy make target:

.. code-block:: shell

	# Check for presence of all prerequisites:
	$ make deps-prerequisites

In case you get any errors please follow the official documentation to install the
missing prerequisite.


Preparing development environment
````````````````````````````````````````````````````````````````````````````````

If you want to participate on the development of this project there is a handy
make target that will make all preparations for you to get you started as soon as
possible. Please execute the following command from the root directory of the
cloned repository to initialize correct Python virtual environment, install all
requirements (including those required only for development) and finally install
the project locally in editable mode:

.. code-block:: shell

	# Initialize Python virtual environmen:
	$ make venv

	# Activate virtual environment before any development work:
	$ . venv/bin/activate

	# Perform all required setup tasks prior to development:
	(venv) $ make develop

	# Deactivate virtual environment when it is not needed anymore with:
	$ deactivate


Dependencies
````````````````````````````````````````````````````````````````````````````````

There is a number of makefile targets called ``deps`` and ``deps-`` that are responsible
for helping with dependency management. Please study the ``make help`` output to
view the list of available targets.

If your code requires some additional third party dependencies please follow these
procedures:

* Python dependencies

  * Use `pip <https://pip.pypa.io/en/stable/reference/>`__ command to manage Python
    dependencies.
  * Dependencies that are always required must be listed in ``conf/requirements.pip``
    file (including version) and in ``conf/requirements-latest.pip`` file (without
    version).
  * Dependencies that are required only for development must be listed in ``conf/requirements-dev.pip``
    file (including version) and in ``conf/requirements-latest-dev.pip`` file (without
    version).

* Web interface dependencies

  * Use `yarn <https://yarnpkg.com/en/docs/usage>`_ command to manage frontend
    dependencies.

Example workflow for adding Python dependency::

	# Install library locally:
	(venv) $ pip install flask

	# Get the version of the library:
	(venv) $ pip freeze | grep -i flask

	# Now write the library name with version to `conf/requirements.pip` and
	# without version to `conf/requirements-latest.pip`.

	# In case the library is required only for development write the library name
	# with version to `conf/requirements-dev.pip` and without version to
	# `conf/requirements-latest-dev.pip`.

	# Make sure the dependency gets installed also using the makefile target:
	(venv) $ make deps-python
	(venv) $ make deps-python-dev

Example workflow for adding frontend dependency::

	# Install dependency with yarn:
	(venv) $ yarn add jquery

	# Install development dependency with yarn:
	(venv) $ yarn add grunt --dev

	# Make sure the dependency gets installed also using the makefile target:
	(venv) $ make deps-webui

For upgrading all the dependencies to latest versions you may use following make
targets::

	# Activate virtual environment before any development work:
	$ . venv/bin/activate

	(venv) $ make deps-python-upgrade
	(venv) $ make deps-python-upgrade-dev
	(venv) $ make deps-webui-upgrade


Running development web server
````````````````````````````````````````````````````````````````````````````````

The web interface for this project is written in excellent `Flask <http://flask.pocoo.org/>`__
microframework, that comes with built-in webserver for development. It can be
launched in following ways::

	# A: You may use the Flask built-in command in a following way:
	(venv) $ FLASK_APP=mydojo FLASK_ENV=development FLASK_CONFIG=development FLASK_CONFIG_FILE=$(realpath ./mydojo.local.conf) flask run

	# B: You may custom command line interface to launch webserver in development
	# mode and with development configuration:
	(venv) $ FLASK_ENV=development FLASK_CONFIG=development FLASK_CONFIG_FILE=$(realpath ./mydojo.local.conf) mydojo-cli run

	# C: Use following makefile target to do the same as the three above with less
	# typing:
	(venv) $ make run-webui-dev

There are following environment variables you may use to tweak the application
launch according to your needs:

* ``FLASK_DEBUG``

  This configuration controls state of the internal debugger independently on the
  ``FLASK_ENV`` setting. It is a boolean value and should be either ``True`` or
  ``False``. Default value is ``False``.

* ``FLASK_ENV``

  This configuration controls application environment setting. This is a string
  value and should be either ``development`` or ``production``. Default value is
  ``production``.

* ``FLASK_CONFIG``

  This configuration controls the name of the configuration class from :py:mod:`mydojo.config`
  module that will be used to configure the application. Valid value is one of the
  :py:attr:`mydojo.config.CONFIG_MAP`. Default value is ``default``.

* ``FLASK_CONFIG_FILE``

  This configuration controls the name of the configuration file that will be used
  to further configure the application. Values in this file are applied last and
  will override anything in the configuration classes from :py:mod:`mydojo.config`.
  Default value is empty. It must point to existing file if set, otherwise an exception
  will be raised. Please use absolute path to the file to avoid any surprises.

.. note::

	The ``FLASK_CONFIG_FILE`` is especially handy for customizing the local
	application configuration during development process or during deployment.

For more information please study following resources:

* `Flask: Command Line Interface <http://flask.pocoo.org/docs/1.0/cli/>`__
* `Flask: Configuration Handling <http://flask.pocoo.org/docs/1.0/config/>`__
* `Flask API: Configuration <http://flask.pocoo.org/docs/1.0/api/#configuration>`__


Documentation
````````````````````````````````````````````````````````````````````````````````

The project documentation consists of the part generated directly from the source
code docstrings and of the part written manually. It is generated using the
`Sphinx-doc <http://www.sphinx-doc.org/en/stable/contents.html>`__ tool into various
formats. Please use `RST <http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`__
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

	# View the documentation in your default web browser:
	(venv) $ make docs-view

	# When necessary you may also remove all documentation related artifacts and
	# rebuild:
	(venv) $ make clean-build-docs
	(venv) $ make docs
	(venv) $ make docs-view

Documentation will be generated into ``doc/build/html/manual.html``.

For more information please study following resources:

* `pydoc3 <https://docs.python.org/3/library/pydoc.html>`__
* `Sphinx-doc <http://www.sphinx-doc.org/en/stable/contents.html>`__

  * `reStructuredText Primer <http://www.sphinx-doc.org/en/stable/rest.html>`__
  * `Sphinx markup constructs <http://www.sphinx-doc.org/en/stable/markup/index.html>`__
  * `The Python domain <http://www.sphinx-doc.org/en/stable/domains.html#the-python-domain>`__
  * `Documenting functions and methods <http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists>`__


Internationalization and translations
````````````````````````````````````````````````````````````````````````````````

The web interface and some other parts of the system are localized to provide best
experience for target user. Following libraries are used to accomplish this task:

* `pybabel <http://babel.pocoo.org/en/latest/index.html>`__
* `flask-babel <https://pythonhosted.org/Flask-Babel/>`__

The web interface translations are included in the :py:mod:`mydojo` module. The most
important files are following:

* ``mydojo/babel.cfg`` - Babel configuration file
* ``mydojo/messages.pot`` - Extracted translations, generated automatically
* ``mydojo/translations/`` - Directory containing translations to various languages

Strings in the python source code are marked for translation when you wrap them
in one of the following functions: ``gettext()``, ``lazy_gettext()``, ``tr_()``.
The last one is defined internally and is used for translating constants or enums.
Strings in the Jinja2 templates are marked for translation when you wrap them with
``gettext()`` or ``_()`` functions.

After adding new strings into the web interface that will need translating please
follow this procedure::

	# Pull (extract and update) all translation strings into message catalogs:
	(venv) $ make pybabel-pull

	# Now please edit the translation files. For example for czech locale please
	# edit file ``mydojo/translations/cs/messages.po``.

	# When you are happy with your translations compile the message catalogs with:
	(venv) $ make pybabel-compile


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


Building web interface
````````````````````````````````````````````````````````````````````````````````

The web interface development requires certain specific tasks like copying third
party libraries from ``node_modules`` directory to correct locations, JavaScript
and CSS minifications etc. When you are developing web interface following makefile
target will be very handy to you:

.. code-block:: shell

	# Always make sure your virtual environment is activated:
	$ . venv/bin/activate

	# Run tests:
	(venv) $ make build-webui


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


Building Python packages
--------------------------------------------------------------------------------

If you want to build native Python packages locally please use following makefile
target:

.. code-block:: shell

	# Always make sure your virtual environment is activated:
	$ . venv/bin/activate

	# Run tests:
	(venv) $ make build-whl

Generated packages will be placed into ``./dist`` subdirectory.
