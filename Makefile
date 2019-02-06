#-------------------------------------------------------------------------------
# MASTER MAKEFILE FOR MYDOJO PACKAGE
#
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

DIR_LIB = mydojo

SPHINXOPTS      =
SPHINXBUILD     = sphinx-build
SPHINXAPIDOC    = sphinx-apidoc
SPHINXPROJ      = MyDojo
SPHINXSOURCEDIR = doc/source
SPHINXBUILDDIR  = doc/build

PYTHON    = python3
PIP       = pip3
NOSETESTS = nosetests
TWINE     = twine
PYBABEL   = pybabel

CURRENT_DIR = $(shell pwd)

#
# Include local customized configurations
#
include Makefile.cfg

#
# Color code definitions for colored terminal output
# https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux
#
RED    = \033[0;31m
GREEN  = \033[0;32m
ORANGE = \033[0;33m
BLUE   = \033[0;34m
PURPLE = \033[0;35m
CYAN   = \033[0;36m
NC     = \033[0m


#-------------------------------------------------------------------------------


#
# Default make target, alias for 'help', you must explicitly choose the target.
#
default: help

#
# Perform all reasonable tasks to do full build.
#
full: docs archive webui bdist deploy

#
# Perform local build.
#
build: archive webui bdist

#
# Check the project code.
#
check: pyflakes pylint test


#-------------------------------------------------------------------------------


help:
	@echo ""
	@echo " ${GREEN}────────────────────────────────────────────────────────────────────────────────${NC}"
	@echo " ${GREEN}                          LIST OF AVAILABLE MAKE TARGETS${NC}"
	@echo " ${GREEN}────────────────────────────────────────────────────────────────────────────────${NC}"
	@echo ""
	@echo "  * ${GREEN}default${NC}: alias for help, you have to pick a target"
	@echo "  * ${GREEN}help${NC}: print this help and exit"
	@echo "  * ${GREEN}show-version${NC}: show current project version"
	@echo "  * ${GREEN}deps${NC}: install various dependencies"
	@echo "     = ${ORANGE}deps-python${NC}: install Python dependencies with pip3"
	@echo "  * ${GREEN}pybabel-patch${NC}: patch babel library"
	@echo "  * ${GREEN}pybabel-extract${NC}: extract translations"
	@echo "  * ${GREEN}pybabel-init INIT_LOCALE=lc${NC}: init translations for given locale lc"
	@echo "  * ${GREEN}pybabel-update${NC}: update translations"
	@echo "  * ${GREEN}pybabel-pull${NC}: extract and update translations"
	@echo "  * ${GREEN}pybabel-compile${NC}: compile translations"
	@echo "  * ${GREEN}full${NC}: generate documentation, archive previous packages and build new distribution"
	@echo "  * ${GREEN}build${NC}: archive previous packages and build new distribution"
	@echo "  * ${GREEN}docs${NC}: generate project docuMyDojoion"
	@echo "     = ${ORANGE}docs-help${NC}: show list of all available html build targets"
	@echo "     = ${ORANGE}docs-html${NC}: generate project docuMyDojoion in HTML format"
	@echo "  * ${GREEN}check${NC}: perform extensive code checking"
	@echo "     = ${ORANGE}pyflakes${NC}: check source code with pyflakes"
	@echo "        - pyflakes-lib: check library with pyflakes, exclude test files"
	@echo "        - pyflakes-test: check test files with pyflakes"
	@echo "     = ${ORANGE}pylint${NC}: check source code with pylint"
	@echo "        - pylint-lib: check library with pylint, exclude test files"
	@echo "        - pylint-test: check test files with pylint"
	@echo "     = ${ORANGE}test${NC}: run unit tests with nosetest"
	@echo "  * ${GREEN}benchmark${NC}: run benchmarks"
	@echo "  * ${GREEN}archive${NC}: archive previous packages"
	@echo "  * ${GREEN}bdist${NC}:   build new distribution"
	@echo "  * ${GREEN}install${NC}: install distribution on local machine"
	@echo "  * ${GREEN}deploy${NC}:  deploy to PyPI"
	@echo ""
	@echo " ${GREEN}────────────────────────────────────────────────────────────────────────────────${NC}"
	@echo ""


#-------------------------------------------------------------------------------


show-version: FORCE
	@PYTHONPATH=. $(PYTHON) -c "import mydojo; print(mydojo.__version__);"


#-------------------------------------------------------------------------------


deps: deps-python

deps-python: FORCE
	@echo "\n${GREEN}*** Installing Python dependencies ***${NC}\n"
	@$(PIP) install -r requirements.pip --upgrade


#-------------------------------------------------------------------------------


#
# This patch solves following issue: https://github.com/python-babel/flask-babel/issues/43
#

pybabel-patch: FORCE
	@echo "\n${GREEN}*** Patching babel library ***${NC}\n"
	@cp util/babel.messages.frontend.py.patch /var/tmp/
	@cd / && patch -p0 -i /var/tmp/babel.messages.frontend.py.patch

#
# When doing translation into another language, you may use following command to
# initialize the translations directory:
#
# 1. Enter directory containing the messages.pot file.
# 2. pybabel init -i messages.pot -d translations -l [locale]
#

pybabel-extract: FORCE
	@echo "\n${GREEN}*** Extracting translations ***${NC}\n"
	@cd $(DIR_LIB) && $(PYBABEL) extract -F babel.cfg -o messages.pot -k lazy_gettext -k tr_ .

pybabel-init: FORCE
	@echo "\n${GREEN}*** Initializing translations for new locale ***${NC}\n"
	@cd $(DIR_LIB) && $(PYBABEL) init -i messages.pot -d translations -l $(INIT_LOCALE)

pybabel-update: FORCE
	@echo "\n${GREEN}*** Updating translations ***${NC}\n"
	@cd $(DIR_LIB) && $(PYBABEL) update -i messages.pot -d translations -l cs

pybabel-pull: hpybabel-extract hpybabel-update

pybabel-compile: FORCE
	@echo "\n${GREEN}*** Compiling translations ***${NC}\n"
	@cd $(DIR_LIB) && $(PYBABEL) compile -d translations


#-------------------------------------------------------------------------------


docs: docs-html

docs-help: FORCE
	@$(SPHINXBUILD) -M help "$(SPHINXSOURCEDIR)" "$(SPHINXBUILDDIR)" $(SPHINXOPTS) $(O)

docs-html: FORCE
	@echo "\n${GREEN}*** Generating project documentation ***${NC}\n"
	@$(SPHINXAPIDOC) -a --force --separate --module-first -o "$(SPHINXSOURCEDIR)/_apidoc" mydojo
	@$(SPHINXBUILD) -M html "$(SPHINXSOURCEDIR)" "$(SPHINXBUILDDIR)" $(SPHINXOPTS) $(O)


#-------------------------------------------------------------------------------


pyflakes: FORCE
	@echo "\n${GREEN}*** Checking code with pyflakes ***${NC}\n"
	@$(PYTHON) --version
	@echo ""
	-@$(PYTHON) -m pyflakes $(DIR_LIB)/*.py

pylint: FORCE
	@echo "\n${GREEN}*** Checking code with pylint ***${NC}\n"
	@$(PYTHON) --version
	@echo ""
	-@$(PYTHON) -m pylint $(DIR_LIB)/*.py --rcfile .pylintrc

test: FORCE
	@echo "\n${GREEN}*** Checking code with nosetests ***${NC}\n"
	@$(NOSETESTS)


#-------------------------------------------------------------------------------


archive: FORCE
	@if ! [ `ls dist/mydojo* | wc -l` = "0" ]; then\
		echo "\n${GREEN}*** Moving old distribution files to archive ***${NC}\n";\
		mkdir -p archive;\
		mv -f dist/mydojo* archive;\
	fi

webui:
	@echo "\n${GREEN}*** Building web interface environment ***${NC}\n"
	@grunt webui

bdist: FORCE
	@echo "\n${GREEN}*** Building Python packages ***${NC}\n"
	@$(PYTHON) --version
	@echo ""
	@$(PYTHON) setup.py release sdist bdist_wheel

install: FORCE
	@echo "\n${GREEN}*** Performing local installation ***${NC}\n"
	@$(PIP) install . --upgrade

install-dev: FORCE
	@echo "\n${GREEN}*** Performing local installation ***${NC}\n"
	@$(PIP) install -e ".[dev]"

deploy: FORCE
	@echo "\n${GREEN}*** Deploying packages to target host ***${NC}\n"
	@/usr/bin/scp dist/mydojo*.whl $(TARGET_HOST):

# Empty rule as dependency will force make to always perform target
# Source: https://www.gnu.org/software/make/manual/html_node/Force-Targets.html
FORCE:
