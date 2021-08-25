SETUP=setup.py
PYTHON=python
TIME=/usr/bin/time -v --
MAIN_FILE=CreateDataset.py


compile:
	$(PYTHON) $(SETUP) build_ext --inplace

debug:compile
	DEBUG=1 $(TIME) $(PYTHON) $(MAIN_FILE)
	
run:compile
	$(TIME) $(PYTHON) $(MAIN_FILE)

