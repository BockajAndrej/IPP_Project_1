# Define Python version and virtual environment
PYTHON=python3.11
VENV=myvenv

# Define source files (optional, useful for linting or testing)
SRC=parse.py

# Default target (runs the project)
all: run

# Create virtual environment and install dependencies
venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip

# Run the Python script using the virtual environment
run: 
	$(VENV)/bin/python $(SRC)

# Run linting (optional)
lint:
	$(VENV)/bin/flake8 $(SRC)

# Run tests (if applicable)
test:
	$(VENV)/bin/pytest tests/

# Clean up the virtual environment
clean:
	rm -rf $(VENV) __pycache__

# Help message
help:
	@echo "Available commands:"
	@echo "  make run      - Run the Python program"
	@echo "  make install  - Install dependencies"
	@echo "  make venv     - Create a virtual environment"
	@echo "  make lint     - Run code linting"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Remove virtual environment and cache files"

