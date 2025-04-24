.PHONY: install test lint format clean run run-ui docs

# Python interpreter to use
PYTHON = python3
# Virtual environment directory
VENV = venv
# Source directory
SRC = app
# Test directory
TEST = tests

# Install dependencies
install:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -r requirements.txt
	. $(VENV)/bin/activate && pip install -r requirements-test.txt

# Run tests
test:
	. $(VENV)/bin/activate && pytest $(TEST)

# Run linting
lint:
	. $(VENV)/bin/activate && flake8 $(SRC)
	. $(VENV)/bin/activate && mypy $(SRC)

# Format code
format:
	. $(VENV)/bin/activate && black $(SRC)
	. $(VENV)/bin/activate && isort $(SRC)

# Clean up
clean:
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

# Run the API application
run:
	. $(VENV)/bin/activate && uvicorn app.main:app --reload

# Run the Streamlit UI
run-ui:
	. $(VENV)/bin/activate && streamlit run app/ui/streamlit_app.py

# Generate documentation
docs:
	. $(VENV)/bin/activate && sphinx-build -b html docs/source docs/build/html

# Run all checks
check: lint test

# Default target
all: install check 