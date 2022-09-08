.PHONY: help all run clean
.DEFAULT_GOAL := run

help: ## Show help text
	@echo "Description:"
	@echo "  Quick build tool"
	@echo ""
	@echo "Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

all: clean install run ## Install libs and run the script

install: ## Install libs
	pip3 install python-redmine python-dotenv janome wordcloud gensim

outdated: ## Show the outdated libs
	pip3 list --outdated

run: ## Run the script (default)
	python3 main.py

clean: ## Delete the existing libs
	rm -rf ./__pycache__

