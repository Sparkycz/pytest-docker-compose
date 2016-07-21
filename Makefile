.PHONY: build configcheck clean test

build: .venv

.venv:
	virtualenv -p `which python3` $(CURDIR)/.venv
	$(CURDIR)/.venv/bin/pip install -r requirements.txt

clean:
	rm -rf $(CURDIR)/.venv

test: build
	$(CURDIR)/.venv/bin/python -m unittest discover
