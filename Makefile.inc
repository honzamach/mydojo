#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

#
# Color code definitions for colored terminal output.
#
# Resource:
#   https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux
#   https://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/x405.html
#   https://linux.die.net/man/1/tput
#
BLACK  = $(shell tput setaf 0)
RED    = $(shell tput setaf 1)
GREEN  = $(shell tput setaf 2)
ORANGE = $(shell tput setaf 3)
BLUE   = $(shell tput setaf 4)
PURPLE = $(shell tput setaf 5)
CYAN   = $(shell tput setaf 6)
WHITE  = $(shell tput setaf 7)
NC     = $(shell tput sgr0)

B_BLACK  = $(shell tput setab 0)
B_RED    = $(shell tput setab 1)
B_GREEN  = $(shell tput setab 2)
B_ORANGE = $(shell tput setab 3)
B_BLUE   = $(shell tput setab 4)
B_PURPLE = $(shell tput setab 5)
B_CYAN   = $(shell tput setab 6)
B_WHITE  = $(shell tput setab 7)

BOLD   = $(shell tput bold)
FAINT  = $(shell tput dim)

#
# Show current project version. This can be used by various automated systems to
# verify/mark the version that is actually being built.
#
show-version: FORCE
	@PYTHONPATH=. $(PYTHON) -c "import $(PROJECT_ID); print($(PROJECT_ID).__version__);"

#
# Show information about current development environment. This may be very handy
# be executed on some automated build systems to determine the state of the build
# environment prior to the build.
#
show-envstamp: FORCE
	@echo "System info: `uname -a`"
	@echo "Python version: `$(PYTHON) --version`"
	@echo "Pip version: `$(PIP) --version`"
	@echo "Yarn version: `yarn --version`"
	@echo "Grunt version: `grunt --version | tr '\n' ','`"
	@echo "Psql version: `psql --version`"
	@echo "Project: $(PROJECT_NAME) ($(PROJECT_ID))"
	@echo "Project version: `PYTHONPATH=lib $(PYTHON) -c 'import $(PROJECT_ID); print($(PROJECT_ID).__version__);'`"
	@echo "Pip libraries:"
	@$(PIP) freeze
