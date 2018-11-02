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

init-db:
	$(FLASK) dropdb
	$(FLASK) db upgrade --directory $(MIGRATIONS)

lint:
	$(PYTEST) --flake8 --isort -m "flake8 or isort" $(FLASK_APP)

migrate:
	$(FLASK) db migrate

serve:
	$(FLASK) run --with-threads -h $(HOST) -p $(PORT)

update-media:
	$(FLASK) update
