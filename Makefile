# Define Python version and virtual environment
PYTHON=python3.11
VENV=myvenv

# Define source files (optional, useful for linting or testing)
SRC=parse.py

# Default target (runs the project)
all: run

# Run the Python script using the virtual environment
run: 
	$(VENV)/bin/python $(SRC) 

i: 
	$(VENV)/bin/python $(SRC) < ./INPUTS/1_sample.SOL25

io: 
	$(VENV)/bin/python $(SRC) < ./INPUTS/1_sample.SOL25 > ./OUTPUTS/1.xml

o: 
	$(VENV)/bin/python $(SRC) > ./OUTPUTS/1.xml

# Run tests (if applicable)
test:
	$(VENV)/bin/pytest tests/

