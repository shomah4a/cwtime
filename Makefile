VENV:=venv
PIP:=$(VENV)/bin/pip

$(VENV)/:
	python3 -m venv venv


install: $(VENV)/
	$(PIP) install -r requirements.txt
