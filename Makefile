include Makefile.config
-include Makefile.custom.config
.SILENT:

clean:
	rm -fr $(VENV)

install:
	test -d $(VENV) || virtualenv $(VENV) -p $(PYTHON_VERSION)
	$(PIP) install -r $(REQUIREMENTS)

init-data:
	$(PYTHON) start_here.py

lint:
	$(PYTEST) --flake8 --isort -m "flake8 or isort"

serve:
	$(FLASK) run --with-threads -h $(HOST) -p $(PORT)
