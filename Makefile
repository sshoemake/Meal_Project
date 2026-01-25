PYTHON := python3.12
VENV := venv

.PHONY: clean venv install up test fresh

clean:
	deactivate
	rm -rf $(VENV)

venv:
	$(PYTHON) -m venv $(VENV)

install:
	source $(VENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

up:
	./compose/up.sh dev

remove:
	./compose/down.sh dev -v

test:
	. $(VENV)/bin/activate && \
	python manage.py test

fresh: clean venv install up test
