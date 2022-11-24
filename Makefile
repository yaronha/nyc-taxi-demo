
PYTHON_INTERPRETER = python3
SHARED_DIR ?= ~/mlrun-data
MLRUN_TAG ?= 1.2.0-rc18
HOST_IP ?=$$(ip route get 1.2.3.4 | awk '{print $$7}')

#################################################################################
# COMMANDS                                                                      #
#################################################################################

.PHONY: help
help: ## Display available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: all
all:
	$(error please pick a target)

.PHONY: install-requirements
install-requirements: ## Install all requirements needed for development
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt -r dev-requirements.txt


.PHONY: package-wheel
package-wheel: clean ## Build python package wheel
	python setup.py bdist_wheel

.PHONY: clean
clean: ## Clean python package build artifacts
	rm -rf build
	rm -rf dist
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

.PHONY: fmt
fmt: ## Format the code (using black and isort)
	@echo "Running black fmt..."
	$(PYTHON_INTERPRETER) -m black src tests
	$(PYTHON_INTERPRETER) -m isort src tests

.PHONY: lint
lint: fmt-check flake8 ## Run lint on the code

.PHONY: fmt-check
fmt-check: ## Format and check the code (using black and isort)
	@echo "Running black+isort fmt check..."
	$(PYTHON_INTERPRETER) -m black --check --diff src tests
	$(PYTHON_INTERPRETER) -m isort --check --diff src tests

.PHONY: flake8
flake8: ## Run flake8 lint
	@echo "Running flake8 lint..."
	$(PYTHON_INTERPRETER) -m flake8 src tests

.PHONY: test
test: clean ## Run tests
	$(PYTHON_INTERPRETER) -m pytest -v --capture=no --disable-warnings -rf tests

.PHONY: start-mlrun
start-mlrun: ## Start MLRun & Nuclio containers
	mkdir $(SHARED_DIR) -p
	SHARED_DIR=$(SHARED_DIR) HOST_IP=$(HOST_IP) TAG=$(MLRUN_TAG) docker-compose -f compose.yaml up -d

.PHONY: stop-mlrun
stop-mlrun: ## Start MLRun & Nuclio containers
	HOST_IP=$(HOST_IP) docker-compose -f compose.yaml down
