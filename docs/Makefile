# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= .venv/bin/python3 -m sphinx
SOURCEDIR     = source
BUILDDIR      = build

VENV=.venv/bin/python3
PIP=.venv/bin/python3 -m pip


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Autobuild sphinx doc every time the file changes.
# Works only on mac: brew install fswatch
watch-mac:
	(while true; do fswatch source/ | make html; done;)


deps: ## Install all dependencies
	@make set_virtualenv
	@$(PIP) install setuptools --upgrade
	@$(PIP) install wheel
	@$(PIP) install -r requirements.txt


set_virtualenv:
ifeq ($(wildcard ./.venv/.*),)
	@echo "Did not find ~/.venv"
	@echo "Now installing virtual env!"
	python3 -m venv .venv
endif

