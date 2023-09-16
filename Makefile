all:

PYTHON=python3

DISPLAY_ON ?= 0
test:
	DISPLAY_ON=${DISPLAY_ON} ${PYTHON} -m test_all 1> output.$@.log

clean:
	@find . -name "*~" | xargs rm -f
	@find . -name "*.pyc" | xargs rm -f
	@find . -name "__pycache__" | xargs rm -rf
	@find . -name "output.*" | xargs rm -f
