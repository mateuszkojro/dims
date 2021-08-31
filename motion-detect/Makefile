SETUP=setup.py
PYTHON=python
TIME=/usr/bin/time -v --
EXEC=CreateDataset.py

install:
	pip install -r requirements.txt

compile:
	$(PYTHON) $(SETUP) build_ext --inplace

debug:
	DEBUG=1 $(TIME) $(PYTHON) $(EXEC) $(FILE)
	
run:
	$(TIME) $(PYTHON) $(EXEC) $(FILE)

html:
	jupyter nbconvert --execute $(FILE) --to html

pdf:
	jupyter nbconvert --execute $(FILE) --to pdf

