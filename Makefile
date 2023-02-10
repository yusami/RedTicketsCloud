.PHONY: help all run clean test
.DEFAULT_GOAL := run

PYTHON := python3
PIP    := pip3
ifeq ($(OS),Windows_NT)
	PYTHON := py
	PIP    := py -m pip
endif
SRCDIR   := src
CACHEDIR := __pycache__
TMPDIR   := tmp
TESTDIR  := test
LIBS     := python-redmine python-dotenv janome wordcloud gensim

help: ## Show help text
	@echo "Description:"
	@echo "  Quick build tool"
	@echo ""
	@echo "Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

all: clean install run test ## Install libs and run the script

install: ## Install libs
	$(PIP) install $(LIBS)

outdated: ## Show the outdated libs
	$(PIP) list --outdated

upgrade: ## Upgrade all libs
	$(PIP) install -U $(LIBS)

info: ## Show the tool version
	@$(PIP) --version
	@$(PYTHON) --version

run: ## Run the script (default)
	$(PYTHON) main.py

test: ## Unit test
	$(PYTHON) -m unittest discover test

clean: ## Delete the cache and tmp files
ifeq ($(OS),Windows_NT)
	if exist $(CACHEDIR) rmdir /s /q $(CACHEDIR)
	if exist $(SRCDIR)\$(CACHEDIR) rmdir /s /q $(SRCDIR)\$(CACHEDIR)
	if exist $(TESTDIR)\$(CACHEDIR) rmdir /s /q $(TESTDIR)\$(CACHEDIR)
	if exist $(TMPDIR) rmdir /s /q $(TMPDIR)
else
	$(RM) -rv ./$(CACHEDIR)
	$(RM) -rv ./$(SRCDIR)/$(CACHEDIR)
	$(RM) -rv ./$(TESTDIR)/$(CACHEDIR)
	$(RM) -rv ./$(TMPDIR)
endif

