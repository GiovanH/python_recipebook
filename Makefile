PY?=python3
PY_FILES=$(wildcard ./*.py) 

.PHONY: doctests pytests

alltests: doctests pytests

doctests:
	$(PY) -m doctest $(PY_FILES)

pytests:
	$(PY) -m pytest $(PY_FILES)

