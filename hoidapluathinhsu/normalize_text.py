import re
import unicodedata


def normalize_unicode_nfc(text):
    """Chuẩn hóa chuỗi Unicode về dạng NFC."""
    if not text:
        return ""
    # 1. Xử lý các ký tự "giả mạo" (Trị dứt điểm lỗi Ðiều 317. Tội vi phạm quy định về vệ sinh an toàn thực phẩm)
    # Ð (U+00D0), ð (U+00F0), ñ (U+00F1)
    mapping = {"\u00d0": "Đ", "\u00f0": "đ", "\u00f1": "đ", "\u00d1": "Đ"}
    for k, v in mapping.items():
        text = text.replace(k, v)
    text = unicodedata.normalize("NFC", text)
    return text


PHU_AM_DAU = [
    "ngh",
    "nh",
    "ph",
    "th",
    "tr",
    "ch",
    "gh",
    "kh",
    "ng",
    "gi",
    "qu",
    "b",
    "c",
    "d",
    "đ",
    "g",
    "h",
    "k",
    "l",
    "m",
    "n",
    "p",
    "r",
    "s",
    "t",
    "v",
    "x",
]
# Nên sắp xếp để đảm bảo khớp đúng:
PHU_AM_DAU_SORTED = sorted(PHU_AM_DAU, key=len, reverse=True)

PHU_AM_CUOI = [
    "ch",
    "nh",
    "ng",
    "t",
    "c",
    "n",
    "m",
    "p",
]
# Sắp xếp để đảm bảo khớp đúng:
PHU_AM_CUOI_SORTED = sorted(PHU_AM_CUOI, key=len, reverse=True)


# Bảng ánh xạ nguyên âm (từ không dấu đến các dạng có dấu và một cột phụ trợ)
# Cột 0: không dấu
# Cột 1: huyền
# Cột 2: sắc
# Cột 3: hỏi
# Cột 4: ngã
# Cột 5: nặng
bang_nguyen_am = [
    ["a", "à", "á", "ả", "ã", "ạ", "a"],
    ["ă", "ằ", "ắ", "ẳ", "ẵ", "ặ", "aw"],
    ["â", "ầ", "ấ", "ẩ", "ẫ", "ậ", "aa"],
    ["e", "è", "é", "ẻ", "ẽ", "ẹ", "e"],
    ["ê", "ề", "ế", "ể", "ễ", "ệ", "ee"],
    ["i", "ì", "í", "ỉ", "ĩ", "ị", "i"],
    ["o", "ò", "ó", "ỏ", "õ", "ọ", "o"],
    ["ô", "ồ", "ố", "ổ", "ỗ", "ộ", "oo"],
    ["ơ", "ờ", "ớ", "ở", "ỡ", "ợ", "ow"],
    ["u", "ù", "ú", "ủ", "ũ", "ụ", "u"],
    ["ư", "ừ", "ứ", "ử", "ữ", "ự", "uw"],
    ["y", "ỳ", "ý", "ỷ", "ỹ", "ỵ", "y"],  # Đảm bảo có 'ỹ'
]

# Từ điển giúp tra cứu nhanh: ánh xạ ký tự nguyên âm (có/không dấu) tới (id_hàng_nguyên_âm, id_cột_dấu)
# Ví dụ: nguyen_am_to_ids['á'] sẽ là (0, 2) nghĩa là hàng 'a', cột 'sắc'
nguyen_am_to_ids = {}
for i, row in enumerate(bang_nguyen_am):
    for j, char in enumerate(row[:-1]):  # Duyệt qua các ký tự nguyên âm có dấu
        nguyen_am_to_ids[char] = (i, j)

# Tập hợp các nguyên âm không dấu (để kiểm tra nhanh)
ALL_UNACCENTED_VOWELS = set([row[0] for row in bang_nguyen_am])


def remove_tone_from_word(word):
    """
    Tách dấu thanh ra khỏi từ.
    - Lấy ID dấu thanh của nguyên âm có dấu ĐẦU TIÊN tìm thấy.
    - Chuyển TẤT CẢ các nguyên âm trong từ về dạng không dấu.
    """
    current_tone_id = 0  # Mặc định là không dấu (0)
    chars_list = list(word)  # Chuyển từ thành list ký tự để dễ sửa đổi

    first_tone_found = False  # Cờ hiệu để chỉ lấy dấu đầu tiên

    for i, char in enumerate(chars_list):
        info = nguyen_am_to_ids.get(char)
        if info:  # Nếu ký tự là một nguyên âm (có dấu hoặc không dấu)
            tone_id = info[1]  # Lấy ID dấu thanh của ký tự đó

            if not first_tone_found and tone_id != 0:
                # Đây là nguyên âm có dấu đầu tiên chúng ta tìm thấy
                current_tone_id = tone_id
                first_tone_found = True  # Đánh dấu đã tìm thấy dấu đầu tiên

            # Luôn chuyển ký tự nguyên âm về dạng không dấu của nó
            # Điều này đảm bảo từ trả về hoàn toàn không có dấu,
            # bất kể có bao nhiêu dấu ban đầu hay vị trí của chúng.
            chars_list[i] = bang_nguyen_am[info[0]][0]

    return "".join(chars_list), current_tone_id


def split_syllable_parts(word_no_tone):
    """
    Tách một từ không dấu thành Phụ âm đầu (PAD), Phần nguyên âm (NA), và Phụ âm cuối (PAC).

    Args:
        word_no_tone (str): Từ đã được bỏ dấu (ví dụ: "hoang", "viet", "qua", "mai", "ch").

    Returns:
        tuple: (PAD, NA, PAC). Ví dụ: ("h", "oa", "ng"), ("v", "ie", "t"), ("", "a", ""), ("m", "ai", ""), ("ch", "", "").
    """
    pad = ""
    pac = ""
    na = ""  # Khởi tạo NA ở đây

    temp_word = word_no_tone  # Dùng biến tạm để thao tác

    # 1. Tách Phụ âm đầu (PAD)
    for p_am_dau in PHU_AM_DAU_SORTED:
        if temp_word.lower().startswith(p_am_dau):
            pad = temp_word[: len(p_am_dau)]  # Giữ nguyên case
            temp_word = temp_word[len(p_am_dau) :]
            break

    # 2. Tách Phụ âm cuối (PAC)
    # temp_word bây giờ là phần còn lại sau PAD (có thể là NA + PAC hoặc chỉ NA, không có đối với trường hợp chữ "gì")
    if temp_word:  # Chỉ kiểm tra nếu còn ký tự sau khi tách PAD
        for p_am_cuoi in PHU_AM_CUOI_SORTED:
            if temp_word.lower().endswith(p_am_cuoi):
                pac = temp_word[len(temp_word) - len(p_am_cuoi) :]
                break

    # 3. Phần còn lại là Phần nguyên âm (NA)
    na = temp_word[: len(temp_word) - len(pac)]

    return pad, na, pac


def apply_tone_to_vowel_char(unaccented_vowel_char, tone_id):
    """Áp dụng dấu thanh vào một ký tự nguyên âm không dấu."""
    for row_id, row in enumerate(bang_nguyen_am):
        if row[0] == unaccented_vowel_char:
            return row[tone_id]
    return unaccented_vowel_char


def normalize_vietnamese_text(text):
    """
    Thêm dấu thanh vào một đoạn văn bản dựa trên logic tách PAD, NA, PAC.
    """
    # Chuẩn hóa Unicode về dạng NFC (khuyến nghị cho mọi xử lý văn bản)
    normalized_text = normalize_unicode_nfc(text)
    tokens = re.findall(r"[a-zA-ZÀ-ỹ]+|\d+|[^\w\s]|\s+", normalized_text)

    clean_words = []  # Biến để nối các từ đã được chỉnh sửa

    for word_token in tokens:
        # Nếu token là dấu câu hoặc khoảng trắng, giữ nguyên
        if not word_token.isalpha() and not word_token.isdigit():
            clean_words.append(word_token)
            continue  # Bỏ qua xử lý logic dấu cho dấu câu/khoảng trắng

        # 1. Lấy từ không dấu và loại dấu ban đầu (nếu có)
        word_no_tone, tone_id = remove_tone_from_word(word_token)

        # 2. Nếu từ không có dấu (tone_id = 0), giữ nguyên và tiếp tục
        if tone_id == 0:
            clean_words.append(word_token)
            continue

        # 3. Tách PAD, NA, PAC
        PAD, NA, PAC = split_syllable_parts(word_no_tone)

        # 4. Kiểm tra NA và áp dụng quy tắc đặt dấu
        final_word = word_token  # Mặc định giữ nguyên nếu không thay đổi được

        if not NA:  # NA rỗng (ví dụ: từ "ch", "ng")
            final_word = (
                word_token  # Giữ nguyên từ gốc đã có dấu (nếu có) hoặc không dấu
            )
        else:
            toned_na_chars = list(NA)  # Chuyển NA thành list để sửa đổi
            target_vowel_index_in_na = -1  # Vị trí nguyên âm để đặt dấu

            num_vowels_in_na = len(NA)

            if num_vowels_in_na == 1:
                target_vowel_index_in_na = 0
            elif num_vowels_in_na == 2:
                if PAC:  # Nếu có PAC, dấu trên nguyên âm thứ 2 của NA
                    target_vowel_index_in_na = 1
                else:  # Không có PAC, dấu trên nguyên âm thứ 1 của NA
                    target_vowel_index_in_na = 0
            elif num_vowels_in_na == 3:
                # Với NA 3 từ, bạn muốn nếu có PAC, bỏ dấu trên NA[2], không có PAC bỏ dấu trên NA[1]
                if PAC:  # Nếu có PAC, dấu trên nguyên âm cuối cùng của NA (NA[2])
                    target_vowel_index_in_na = 2
                else:  # Không có PAC, dấu trên nguyên âm thứ hai của NA (NA[1])
                    target_vowel_index_in_na = 1

            # Áp dụng dấu nếu tìm thấy vị trí hợp lệ
            if target_vowel_index_in_na != -1 and target_vowel_index_in_na < len(
                toned_na_chars
            ):
                original_vowel = toned_na_chars[target_vowel_index_in_na]
                toned_char = apply_tone_to_vowel_char(original_vowel, tone_id)
                toned_na_chars[target_vowel_index_in_na] = toned_char
                final_word = PAD + "".join(toned_na_chars) + PAC
            else:
                final_word = (
                    word_token  # Trường hợp lỗi hoặc không thể đặt dấu, giữ nguyên
                )

        clean_words.append(final_word)

    return "".join(clean_words)  # Nối các tokens đã xử lý lại



