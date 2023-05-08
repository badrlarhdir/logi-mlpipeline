.PHONY: clean format check install uninstall test pypi

venv:
	which python3
	python3 -m venv venv

clean:
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	find . -name "*pycache*" | xargs rm -rf

format:
	black mlpipeline
	blackdoc mlpipeline
	isort mlpipeline

check:
	black mlpipeline --check --diff
	blackdoc mlpipeline --check
	flake8 --config pyproject.toml --ignore E203,E501,W503 mlpipeline
	mypy --config pyproject.toml mlpipeline
	isort mlpipeline --check --diff

install:
	python3 setup.py install

uninstall:
	python3 -m pip uninstall mlpipeline -y

test:
	python3 -m pytest --doctest-modules
