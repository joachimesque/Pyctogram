include Makefile.config
-include Makefile.custom.config
.SILENT:

clean:
	rm -fr $(VENV)

prepare-install:
	python3 -m venv $(VENV)

install:
	test -d $(VENV) || virtualenv $(VENV) -p $(PYTHON_VERSION)
	$(PIP) install -r $(REQUIREMENTS)

init-db:
	$(FLASK) dropdb
	$(FLASK) db upgrade --directory $(MIGRATIONS)

lint:
	$(PYTEST) --flake8 --isort -m "flake8 or isort" $(FLASK_APP)

migrate:
	$(FLASK) db migrate

run:
	FLASK_ENV=production && $(GUNICORN) -b $(HOST):$(PORT) "$(FLASK_APP):create_app()" --error-logfile $(GUNICORN_LOG)

serve:
	$(FLASK) run --with-threads -h $(HOST) -p $(PORT)

update-db:
	$(FLASK) db upgrade --directory $(MIGRATIONS)

update-media:
	$(FLASK) update
