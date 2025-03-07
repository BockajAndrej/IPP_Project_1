# Define Python version and virtual environment
PYTHON=python3.11
VENV=myvenv
TESTVENT=.venv

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
	. ./tests/.venv/bin/activate && pytest ./tests
test_arg:
	. ./tests/.venv/bin/activate && pytest ./tests/test_args.py

test_lex:
	. ./tests/.venv/bin/activate && pytest ./tests/test_lex.py

test_syn:
	. ./tests/.venv/bin/activate && pytest ./tests/test_syntax.py

test_sem:
	. ./tests/.venv/bin/activate && pytest ./tests/test_sem.py

test_val:
	. ./tests/.venv/bin/activate && pytest ./tests/test_valid.py

