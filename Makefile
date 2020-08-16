# MAKEFLAGS+=.silent

SRC_DIR=concat

all:

# TODO: Automate testing. Setup pytest workflow
test:
	cd test && concat A.c >/dev/null && diff example.c concated.c

check-unused-imports:
	find ${SRC_DIR} -type f -name "*.py" | xargs pylint --disable=all --enable=W0611

# Set alias for easy typing
cui: check-unused-imports

reformat:
	isort --apply
	black .

lint:
	find ${TEST_DIR} -type f -name "*.py" | xargs pylint

todo:
	rg -ri TODO

.PHONY: all test check-unused-imports cui reformat lint todo
