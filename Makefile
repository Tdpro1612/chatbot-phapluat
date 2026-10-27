VENV = .venv
PYTHON_VENV = ./$(VENV)/bin/python
PIP_VENV = ./$(VENV)/bin/pip

install:
	@echo "==> Đang tạo môi trường ảo $(VENV)..."
	python3 -m venv $(VENV)
	@echo "==> Đang nâng cấp pip và cài đặt thư viện từ pyproject.toml..."
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -e .
	@echo "==> Cài đặt hoàn tất!"

format:
	@echo "==> Đang làm sạch và định dạng code bằng isort & black..."
	$(VENV)/bin/isort src/
	$(VENV)/bin/black src/

run-api:
	@echo "==> Đang khởi động FastAPI Service (Agent 3)..."
	$(VENV)/bin/uvicorn src.api.main:app --reload

clean:
	@echo "==> Đang dọn dẹp môi trường ảo và cache..."
	rm -rf $(VENV)
	rm -rf __pycache__ .pytest_cache
	find . -type f -name "*.pyc" -delete
	@echo "==> Dọn dẹp xong!"