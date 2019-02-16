#-------------------------------------------------------------------------------
# MASTER MAKEFILE FOR MYDOJO PROJECT
#
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Author: Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


#
# Default make target, alias for 'help', you must explicitly choose the target.
#
default: help


#===============================================================================


PROJECT_ID   = mydojo
PROJECT_NAME = MyDojo

DIR_LIB = $(PROJECT_ID)

SPHINXOPTS      =
SPHINXBUILD     = sphinx-build
SPHINXAPIDOC    = sphinx-apidoc
SPHINXPROJ      = $(PROJECT_NAME)
SPHINXSOURCEDIR = doc/source
SPHINXBUILDDIR  = doc/build

VENV_PYTHON = python3
VENV_PATH   = venv
PYTHON      = python
PIP         = pip
NOSETESTS   = nosetests
PYBABEL     = pybabel

CURRENT_DIR = $(shell pwd)

#
# Include common makefile configurations.
#
include Makefile.inc

#
# Include local customized configurations.
#
include Makefile.cfg


#===============================================================================


#
# Display extensive help information page.
#
help:
	@echo ""
	@echo "                 ███╗   ███╗██╗   ██╗██████╗  ██████╗      ██╗ ██████╗ "
	@echo "                 ████╗ ████║╚██╗ ██╔╝██╔══██╗██╔═══██╗     ██║██╔═══██╗"
	@echo "                 ██╔████╔██║ ╚████╔╝ ██║  ██║██║   ██║     ██║██║   ██║"
	@echo "                 ██║╚██╔╝██║  ╚██╔╝  ██║  ██║██║   ██║██   ██║██║   ██║"
	@echo "                 ██║ ╚═╝ ██║   ██║   ██████╔╝╚██████╔╝╚█████╔╝╚██████╔╝"
	@echo "                 ╚═╝     ╚═╝   ╚═╝   ╚═════╝  ╚═════╝  ╚════╝  ╚═════╝ "
	@echo "             $(FAINT)Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>$(NC)"
	@echo ""
	@echo " $(GREEN)$(BOLD)╔═════════════════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo " $(GREEN)$(BOLD)║                           LIST OF AVAILABLE MAKE TARGETS                            ║$(NC)"
	@echo " $(GREEN)$(BOLD)╚═════════════════════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "  $(BLUE)$(BOLD)MAIN TARGETS$(NC)"
	@echo "  $(BLUE)$(BOLD)────────────$(NC)"
	@echo "  * $(GREEN)default$(NC): alias for help, you must pick a target"
	@echo "  * $(GREEN)help$(NC): print this extensive help text and exit"
	@echo "  * $(GREEN)show-version$(NC): show current project version"
	@echo "  * $(GREEN)show-envstamp$(NC): show information about current development environment"
	@echo "  * $(GREEN)develop$(NC): install and configure project locally for development"
	@echo "  * $(GREEN)deps$(NC): install project dependencies"
	@echo "  * $(GREEN)clean$(NC): cleanup development and build environment"
	@echo "  * $(GREEN)docs$(NC): generate project documentation"
	@echo "  * $(GREEN)check$(NC): perform all checks and tests"
	@echo "  * $(GREEN)build-whl$(NC): perform local build of Python distribution package"
	@echo ""
	@echo "  $(BLUE)$(BOLD)HELPER TARGETS$(NC)"
	@echo "  $(BLUE)$(BOLD)──────────────$(NC)"
	@echo "  * $(GREEN)deps-prerequisites$(NC): check for development prerequisites"
	@echo "  * $(GREEN)deps-python$(NC): install Python dependencies"
	@echo "  * $(GREEN)deps-python-dev$(NC): install Python development dependencies"
	@echo "  * $(GREEN)deps-python-upgrade$(NC): upgrade Python dependencies to latest versions"
	@echo "  * $(GREEN)deps-python-upgrade-dev$(NC): upgrade Python development dependencies to latest versions"
	@echo "  * $(GREEN)deps-webui$(NC): install web interface dependencies"
	@echo "  * $(GREEN)deps-webui-upgrade$(NC): upgrade web interface dependencies"
	@echo "  * $(GREEN)deps-postgresql$(NC): configure required PostgreSQL user accounts and databases"
	@echo ""
	@echo "  * $(GREEN)clean-pycs$(NC): clean up Python compiled files"
	@echo "  * $(GREEN)clean-build-docs$(NC): clean up documentation build directories"
	@echo "  * $(GREEN)clean-build-python$(NC): clean up Python build directories"
	@echo ""
	@echo "  * $(GREEN)docs-html$(NC): generate project documentation in HTML"
	@echo "  * $(GREEN)docs-view$(NC): view project documentation in HTML"
	@echo ""
	@echo "  * $(GREEN)pybabel-patch$(NC): patch babel library"
	@echo "  * $(GREEN)pybabel-init INIT_LOCALE=lc$(NC): init translations for given locale $(FAINT)lc$(NC)"
	@echo "  * $(GREEN)pybabel-pull$(NC): extract and update translations"
	@echo "      - $(ORANGE)pybabel-extract$(NC): extract translations"
	@echo "      - $(ORANGE)pybabel-update$(NC): update translations"
	@echo "  * $(GREEN)pybabel-compile$(NC): compile translations"
	@echo ""
	@echo "  * $(GREEN)check-pyflakes$(NC): check project with pyflakes"
	@echo "  * $(GREEN)check-pylint$(NC): check project with pylint"
	@echo "  * $(GREEN)check-test$(NC): run unit tests with nosetest"
	@echo ""
	@echo "  * $(GREEN)build-webui$(NC): setup web interface locally"
	@echo "  * $(GREEN)build-package-whl$(NC): actually generate Python package"
	@echo ""
	@echo "  * $(GREEN)deploy$(NC): deploy to remote server"
	@echo ""

	@echo " $(GREEN)═══════════════════════════════════════════════════════════════════════════════════════$(NC)"
	@echo ""


#-------------------------------------------------------------------------------


#
# Install and configure project locally for development. This target will perform
# following tasks for you:
#   - bootstrap the Python virtual environment into 'venv' subdirectory
#   - install all requirements (etc/requirements.pip)
#   - install all development requirements (etc/requirements-dev.pip)
#   - install the project in editable mode
#
# NOTE: This target is calling 'venv/bin/activate' on its own to install the
# requirements into newly created/existing virtual environment. When using all
# other makefile targets you must enable the environment youself!
#
develop: FORCE
	@echo "\n$(GREEN)*** Installing Python virtual environment for local development ***$(NC)\n"
	@echo "Requested version: $(VENV_PYTHON)"
	@echo "Path to binary:    `which $(VENV_PYTHON)`"
	@echo "Path to venv:      $(VENV_PATH)"
	@echo ""
	@if [ -d $(VENV_PATH) ]; then\
		echo "$(CYAN)Virtual environment already exists in '$(VENV_PATH)'.$(NC)";\
	else\
		$(VENV_PYTHON) -m venv $(VENV_PATH);\
		echo "$(CYAN)Virtual environment successfully created in '$(VENV_PATH)'.$(NC)";\
	fi
	@echo ""
	@echo "Venv path: `. $(VENV_PATH)/bin/activate && python -c 'import sys; print(sys.prefix)'`"
	@echo "Python stuff versions:"
	@echo ""
	@ls -al $(VENV_PATH)/bin | grep python
	@ls -al $(VENV_PATH)/bin | grep pip

	@echo "\n$(GREEN)*** Installing project requirements ***$(NC)\n"
	@. $(VENV_PATH)/bin/activate && $(PIP) install -r etc/requirements.pip

	@echo "\n$(GREEN)*** Installing project development requirements ***$(NC)\n"
	@. $(VENV_PATH)/bin/activate && $(PIP) install -r etc/requirements-dev.pip

	@echo "\n$(GREEN)*** Installing project into virtual environment in editable mode ***$(NC)\n"
	@. $(VENV_PATH)/bin/activate && $(PIP) install -e ".[dev]"

	@echo "\n$(CYAN)Your development environment is ready in `. $(VENV_PATH)/bin/activate && python -c 'import sys; print(sys.prefix)'`.$(NC)\n"
	@echo "Please activate it manually with following command:\n"
	@echo "\t$(ORANGE). $(VENV_PATH)/bin/activate$(NC)\n"
	@echo "!!! Please keep in mind, that all makefile targets leave it up to you to activate the correct virtual environment !!!"
	@echo ""

#
# Install and configure project dependencies.
#
deps: deps-prerequisites deps-python deps-python-dev deps-webui deps-postgresql pybabel-compile

#
# Cleanup development and build environment.
#
clean: clean-pycs clean-build-docs clean-build-python

#
# Generate project documentation.
#
docs: docs-html

#
# Check the project code.
#
check: pyflakes pylint test

#
# Perform local build.
#
build-whl: clean build-webui build-package-whl


#===============================================================================


#
# Check for development prerequisites. The prerequisites are certain commands and
# applications that have to be already installed on local system, otherwise the
# installation can not proceed further. These prerequisites ussually require more
# complex installation process, or their installation is not straightforward, or
# there are multiple installation procedures and it is not possible to choose the
# best option. In any case, it is best to leave the installation to the user.
#
deps-prerequisites: FORCE
	@echo "\n$(GREEN)*** Checking for development prerequisites ***$(NC)\n"
	@for prereq in $(PYTHON) $(PIP) yarn grunt psql ; do \
		if command -v $$prereq >/dev/null 2>&1; then \
			echo "Prerequisite: $$prereq (`$$prereq --version | tr '\n' ',' | sed -e s/,$$//g;`)"; \
		else \
			echo "$(RED)PREREQUISITE: $$prereq (missing).$(NC)\n"; \
			echo "You have to install this prerequisite manually.\n"; \
			exit 1; \
		fi \
	done
	@echo ""

#
# Install project`s Python dependencies using pip requirements file. The dependencies
# are already listed in setup.py file and pip can install them automatically. It
# is however better to use requirements file directly, because its syntax enables
# users to provide addditonal options to pip binary and thus enable for example
# an installation of binary packages. It is much more powerfull than simple syntax
# of 'install_requires' keyword of 'setup.py'.
#
deps-python: FORCE
	@echo "\n$(GREEN)*** Installing Python dependencies ***$(NC)\n"
	@$(PIP) --version
	@$(PIP) install -r etc/requirements.pip --upgrade
	@echo ""

#
# Install project`s Python development dependencies using pip requirements file.
# These dependencies are essential for development, but not required for production
# deployment. For more information on why to use pip requirements file explicitly
# instead of letting it install the dependencies from the list in 'setup.py' file
# please see the documentation of 'deps-python' target above.
#
deps-python-dev: FORCE
	@echo "\n$(GREEN)*** Installing Python development dependencies ***$(NC)\n"
	@$(PIP) --version
	@$(PIP) install -r etc/requirements-dev.pip
	@echo ""

#
# Upgrade project`s Python dependencies using pip requirements file to latest
# versions.
#
deps-python-upgrade: FORCE
	@echo "\n$(GREEN)*** Upgrading Python dependencies to latest versions ***$(NC)\n"
	@$(PIP) --version
	@$(PIP) install -r etc/requirements-latest.pip --upgrade
	@echo ""

#
# Upgrade project`s Python development dependencies using pip requirements file
# to latest versions. These dependencies are essential for development, but not
# required for production deployment.
#
deps-python-upgrade-dev: FORCE
	@echo "\n$(GREEN)*** Upgrading Python development dependencies to latest versions ***$(NC)\n"
	@$(PIP) --version
	@$(PIP) install -r etc/requirements-latest-dev.pip --upgrade
	@echo ""

#
# Install project`s web interface dependencies using yarn.
#
deps-webui: FORCE
	@echo "\n$(GREEN)*** Installing web interface dependencies ***$(NC)\n"
	@yarn install
	@echo ""

#
# Upgrade project`s web interface dependencies using yarn to latest versions.
#
deps-webui-upgrade: FORCE
	@echo "\n$(GREEN)*** Upgrading web interface dependencies ***$(NC)\n"
	@yarn upgrade
	@echo ""

#
# Create and configure required PostgreSQL user accounts and databases.
#
deps-postgresql: FORCE
	@echo "\n$(GREEN)*** Configuring required PostgreSQL user accounts and databases ***$(NC)\n"
	@./bin/mydojo-init.sh
	@echo ""


#-------------------------------------------------------------------------------


run-webui-dev:
	@echo "\n$(GREEN)*** Running development web server with development configuration ***$(NC)\n"
	@FLASK_ENV=development FLASK_CONFIG=development FLASK_CONFIG_FILE=$(shell realpath ./$(PROJECT_ID).local.conf) $(PROJECT_ID)-cli run


#-------------------------------------------------------------------------------

#
# Get rid of all precompiled Python files and '~' backup files.
#
clean-pycs: FORCE
	@echo "\n$(GREEN)*** Cleaning up Python precompiled files ***$(NC)\n"
	@find . -name '*.pyc' -delete
	@find . -name '*.pyo' -delete
	@find . -name '*~' -delete
	@echo ""

clean-build-docs: FORCE
	@echo "\n$(GREEN)*** Cleaning up documentation build directories ***$(NC)\n"
	@rm --force --recursive doc/build/
	@rm --force --recursive doc/source/_apidoc/
	@echo ""

clean-build-python: FORCE
	@echo "\n$(GREEN)*** Cleaning up Python build directories ***$(NC)\n"
	@rm --force --recursive build/
	@rm --force --recursive dist/
	@rm --force --recursive *.egg-info
	@echo ""


#-------------------------------------------------------------------------------


docs-help: FORCE
	@$(SPHINXBUILD) -M help "$(SPHINXSOURCEDIR)" "$(SPHINXBUILDDIR)" $(SPHINXOPTS) $(O)
	@echo ""

docs-html: FORCE
	@echo "\n$(GREEN)*** Generating project API documentation ***$(NC)\n"
	@$(SPHINXAPIDOC) --force --separate --module-first -o "$(SPHINXSOURCEDIR)/_apidoc" mydojo

	@echo "\n$(GREEN)*** Generating project documentation - HTML ***$(NC)\n"
	@$(SPHINXBUILD) -M html "$(SPHINXSOURCEDIR)" "$(SPHINXBUILDDIR)" $(SPHINXOPTS) $(O)
	@echo ""

docs-view: FORCE
	@echo "\n$(GREEN)*** Displaying project documentation ***$(NC)\n"
	@x-www-browser $(SPHINXBUILDDIR)/html/manual.html


#-------------------------------------------------------------------------------


#
# This patch solves following issue: https://github.com/python-babel/flask-babel/issues/43
#

pybabel-patch: FORCE
	@echo "\n$(GREEN)*** Patching babel library ***$(NC)\n"
	@cp util/babel.messages.frontend.py.patch /var/tmp/
	@cd / && patch -p0 -i /var/tmp/babel.messages.frontend.py.patch
	@echo ""

#
# When doing translation into another language, you may use following command to
# initialize the translations directory:
#
# 1. Enter directory containing the messages.pot file.
# 2. pybabel init -i messages.pot -d translations -l [locale]
#

pybabel-extract: FORCE
	@echo "\n$(GREEN)*** Extracting translations ***$(NC)\n"
	@cd $(DIR_LIB) && $(PYBABEL) extract -F babel.cfg -o messages.pot -k lazy_gettext -k tr_ .
	@echo ""

pybabel-init: FORCE
	@echo "\n$(GREEN)*** Initializing translations for new locale ***$(NC)\n"
	@cd $(DIR_LIB) && $(PYBABEL) init -i messages.pot -d translations -l $(INIT_LOCALE)
	@echo ""

pybabel-update: FORCE
	@echo "\n$(GREEN)*** Updating translations ***$(NC)\n"
	@cd $(DIR_LIB) && $(PYBABEL) update -i messages.pot -d translations -l cs
	@echo ""

pybabel-pull: pybabel-extract pybabel-update

pybabel-compile: FORCE
	@echo "\n$(GREEN)*** Compiling translations ***$(NC)\n"
	@cd $(DIR_LIB) && $(PYBABEL) compile -d translations
	@echo ""


#-------------------------------------------------------------------------------


pyflakes: FORCE
	@echo "\n$(GREEN)*** Checking code with pyflakes ***$(NC)\n"
	@echo "Python version: `$(PYTHON) --version`"
	@echo "Project path:   `$(PYTHON) -c 'import mydojo; import os; print(os.path.abspath(mydojo.__file__));'`"
	@echo ""
	-@$(PYTHON) -m pyflakes $(DIR_LIB)/*.py
	@echo ""

pylint: FORCE
	@echo "\n$(GREEN)*** Checking code with pylint ***$(NC)\n"
	@echo "Python version: `$(PYTHON) --version`"
	@echo "Project path:   `$(PYTHON) -c 'import mydojo; import os; print(os.path.abspath(mydojo.__file__));'`"
	@echo ""
	-@$(PYTHON) -m pylint $(DIR_LIB)/*.py --rcfile .pylintrc
	@echo ""

test: FORCE
	@echo "\n$(GREEN)*** Checking code with nosetests ***$(NC)\n"
	@echo "Python version: `$(PYTHON) --version`"
	@echo "Project path:   `$(PYTHON) -c 'import mydojo; import os; print(os.path.abspath(mydojo.__file__));'`"
	@$(NOSETESTS)
	@echo ""


#-------------------------------------------------------------------------------


build-webui: FORCE
	@echo "\n$(GREEN)*** Building web interface environment ***$(NC)\n"
	@grunt webui
	@echo ""

build-package-whl: FORCE
	@echo "\n$(GREEN)*** Building Python packages ***$(NC)\n"
	@echo "Python version: `$(PYTHON) --version`"
	@echo ""
	@$(PYTHON) setup.py sdist bdist_wheel
	@echo ""

deploy: FORCE
	@echo "\n$(GREEN)*** Deploying packages to target host ***$(NC)\n"
	@/usr/bin/scp dist/mydojo*.whl $(TARGET_HOST):
	@echo ""


# Empty rule as dependency will force make to always perform target
# Source: https://www.gnu.org/software/make/manual/html_node/Force-Targets.html
FORCE:
