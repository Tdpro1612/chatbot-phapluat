VENV = law
PYTHON_SYS = python3
# PYTHON_VENV là python sau khi đã cài xong môi trường
PYTHON_VENV = $(VENV)/bin/python3
PIP_VENV = $(VENV)/bin/pip

install:
	# Dùng python hệ thống để tạo venv
	$(PYTHON_SYS) -m venv $(VENV)
	# Sau đó mới dùng pip của venv để cài thư viện
	$(PIP_VENV) install -r requirements.txt
	# coi thư mục là 1 pagkage để có thể import được
	$(PYTHON_VENV) -m pip install -e .


format:
	$(VENV)/bin/isort .
	$(VENV)/bin/black .

lint:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/pylint --ignore=$(VENV) $$(git ls-files '*.py')

all: format lint