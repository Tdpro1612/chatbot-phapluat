# test no log if pass
pytest tests/test_normalize_text.py
# test full log 
pytest -o "log_cli=true" --log-cli-level=INFO tests/test_normalize_text.py



