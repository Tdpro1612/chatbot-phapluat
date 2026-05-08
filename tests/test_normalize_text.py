import logging
import pytest
from hoidapluathinhsu.normalize_text import normalize_unicode_nfc, normalize_vietnamese_text

# Cấu hình log
logging.basicConfig(level=logging.INFO, format='%(message)s')

# --- TEST CHO NFC & KÝ TỰ LỖI ---
@pytest.mark.parametrize("input_text, expected_output", [
    ("Ðiều 317", "Điều 317"), # Lỗi chữ Ð (U+00D0)
    ("ñiều", "điều"),         # Lỗi chữ ñ
])
def test_normalize_unicode_nfc(input_text, expected_output):
    result = normalize_unicode_nfc(input_text)
    logging.info(f"NFC In: {input_text} -> Out: {result}")
    assert result == expected_output  

# --- TEST CHO TOÀN BỘ LOGIC (VỊ TRÍ DẤU) ---
@pytest.mark.parametrize("input_text, expected_output", [
    ("hòa bình", "hòa bình"),  # Kiểm tra giữ nguyên kiểu mới
    ("hoà bình", "hòa bình"),  # Kiểm tra chuyển từ cũ sang mới
    ("quả", "quả"),            # Kiểm tra trường hợp 'qu'
    ("uýnh", "uýnh")           # Kiểm tra trường hợp 'uý'
])
def test_normalize_vietnamese_text(input_text, expected_output):
    result = normalize_vietnamese_text(input_text)
    logging.info(f"Full In: {input_text} -> Out: {result}")
    assert result == expected_output  