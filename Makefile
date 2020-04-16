# MAKEFLAGS+=.silent

SRC_DIR=concat

all:

test:
	python -m concat test/A.c

check-unused-imports:
	find ${SRC_DIR} -type f -name "*.py" | xargs pylint --disable=all --enable=W0611

# Set alias for easy typing
cui: check-unused-imports

reformat:
	find ${SRC_DIR} -type f -name "*.py" | xargs isort
	black .

lint:
	find ${TEST_DIR} -type f -name "*.py" | xargs pylint

todo:
	grep -ri --include=*.py TODO

.PHONY: all test reformat lint