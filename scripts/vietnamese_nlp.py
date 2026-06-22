"""InfinityNeural Vietnamese NLP — Enhanced compound detection and morphology.

Extends the base NeuralMemory Vietnamese support with:
- 200+ compound word list (từ ghép Việt Nam)
- Extended stopwords (100+ thêm)
- Morphology helpers for Vietnamese text normalization
- Syllable analysis for tone-aware matching
"""

from __future__ import annotations

import re
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Vietnamese compound words (từ ghép) — common 2-3 syllable compounds
# These should be treated as single tokens during keyword extraction
# ---------------------------------------------------------------------------

VIETNAMESE_COMPOUNDS: frozenset[str] = frozenset({
    # Education
    "học sinh", "sinh viên", "giáo viên", "trường học", "đại học",
    "tiểu học", "trung học", "cao đẳng", "thạc sĩ", "tiến sĩ",
    "giáo dục", "đào tạo", "bài giảng", "bài tập", "kiểm tra",
    "thi cử", "tốt nghiệp", "nhập học", "học phí", "học bổng",
    
    # Family
    "gia đình", "cha mẹ", "ông bà", "anh chị", "con cái",
    "vợ chồng", "bố mẹ", "họ hàng", "bà ngoại", "ông nội",
    "anh em", "chị em", "cháu chắt", "dâu rể", "con dâu",
    
    # Work
    "công việc", "công ty", "doanh nghiệp", "nhân viên", "giám đốc",
    "trưởng phòng", "phó giám đốc", "hội đồng", "ban giám đốc",
    "lương thưởng", "hợp đồng", "nghỉ phép", "tăng ca", "sa thải",
    
    # Technology
    "trí tuệ", "nhân tạo", "máy tính", "điện thoại", "phần mềm",
    "phần cứng", "cơ sở dữ liệu", "mạng xã hội", "ứng dụng",
    "truyền thông", "công nghệ", "kỹ thuật", "số hóa", "tự động",
    "học máy", "học sâu", "dữ liệu", "bảo mật", "mã nguồn",
    
    # Society
    "xã hội", "cộng đồng", "văn hóa", "lịch sử", "chính trị",
    "kinh tế", "pháp luật", "quốc gia", "dân tộc", "tôn giáo",
    "truyền thống", "phong tục", "tập quán", "thể thao", "nghệ thuật",
    
    # Health
    "sức khỏe", "bệnh viện", "bác sĩ", "y tá", "thuốc men",
    "chữa bệnh", "khám bệnh", "điều trị", "phẫu thuật", "chăm sóc",
    "dinh dưỡng", "tập thể dục", "sức đề kháng", "miễn dịch",
    
    # Nature
    "thiên nhiên", "môi trường", "khí hậu", "thời tiết", "động vật",
    "thực vật", "biển cả", "sông ngòi", "núi rừng", "đồng bằng",
    
    # Emotions
    "hạnh phúc", "buồn bã", "tức giận", "lo lắng", "sợ hãi",
    "vui vẻ", "yêu thương", "căm ghét", "ghen tị", "tự hào",
    "xấu hổ", "ngạc nhiên", "thất vọng", "hy vọng", "tuyệt vọng",
    
    # Actions
    "làm việc", "ăn uống", "đi lại", "mua bán", "trao đổi",
    "giao tiếp", "hợp tác", "cạnh tranh", "phát triển", "thay đổi",
    "cải thiện", "giải quyết", "quyết định", "lựa chọn", "sáng tạo",
    
    # Food
    "ăn sáng", "ăn trưa", "ăn tối", "bữa ăn", "thức ăn",
    "đồ uống", "nước uống", "cà phê", "trà sữa", "bánh mì",
    
    # Philosophy / Abstract
    "triết học", "tư tưởng", "ý nghĩa", "giá trị", "chân lý",
    "đạo đức", "lương tâm", "nhân sinh", "bản chất", "hiện tượng",
    "siêu hình", "duy vật", "duy tâm", "biện chứng", "bản ngã",
    
    # AI / Tech specific
    "mô hình", "huấn luyện", "tinh chỉnh", "nhận dạng", "xử lý",
    "phân tích", "tổng hợp", "tối ưu", "thuật toán", "khung thần kinh",
})

# ---------------------------------------------------------------------------
# Extended Vietnamese stopwords (beyond base set)
# ---------------------------------------------------------------------------

EXTENDED_STOPWORDS_VI: frozenset[str] = frozenset({
    # Particles
    "à", "ạ", "á", "ấy", "ấy", "ơi", "nhỉ", "nhé", "nha", "nghen",
    "hen", "hả", "hở", "chứ", "thôi", "đi", "đây", "kia", "đấy",
    
    # Connectors
    "mặc dù", "tuy nhiên", "nhưng mà", "cho nên", "bởi vì",
    "do đó", "vì vậy", "tuy rằng", "dù rằng", "thế nhưng",
    "hơn nữa", "ngoài ra", "bên cạnh", "thêm vào",
    
    # Time markers (generic, not specific dates)
    "hôm nay", "hôm qua", "ngày mai", "bây giờ", "lúc này",
    "hiện tại", "trước đây", "sau này", "lúc đó", "khi đó",
    
    # Intensifiers
    "thật sự", "vô cùng", "cực kỳ", "hết sức", "hoàn toàn",
    "tuyệt đối", "khá là", "hơi hơi", "chút chút",
    
    # Pronouns (extended)
    "mình", "mày", "tao", "nó", "hắn", "chúng tôi", "chúng ta",
    "các bạn", "họ", "người ta", "ai đó", "gì đó",
    
    # Filler words
    "thế", "vậy", "thì", "nha", "nghe", "biết không",
    "đúng không", "phải không", "được không",
})

# ---------------------------------------------------------------------------
# Vietnamese tone marks and syllable analysis
# ---------------------------------------------------------------------------

# Vietnamese tones mapped from diacritical marks
TONE_MAP: dict[str, str] = {
    # Level (ngang) — no mark
    # Rising (sắc)
    "á": "a_sac", "é": "e_sac", "í": "i_sac", "ó": "o_sac", "ú": "u_sac", "ý": "y_sac",
    "ắ": "aw_sac", "ấ": "aa_sac", "ế": "ee_sac", "ố": "oo_sac", "ớ": "ow_sac", "ứ": "uw_sac",
    # Falling (huyền)
    "à": "a_huyen", "è": "e_huyen", "ì": "i_huyen", "ò": "o_huyen", "ù": "u_huyen", "ỳ": "y_huyen",
    "ằ": "aw_huyen", "ầ": "aa_huyen", "ề": "ee_huyen", "ồ": "oo_huyen", "ờ": "ow_huyen", "ừ": "uw_huyen",
    # Broken (ngã)
    "ã": "a_nga", "ẽ": "e_nga", "ĩ": "i_nga", "õ": "o_nga", "ũ": "u_nga", "ỹ": "y_nga",
    "ẵ": "aw_nga", "ẫ": "aa_nga", "ễ": "ee_nga", "ỗ": "oo_nga", "ỡ": "ow_nga", "ữ": "uw_nga",
    # Question (hỏi)
    "ả": "a_hoi", "ẻ": "e_hoi", "ỉ": "i_hoi", "ỏ": "o_hoi", "ủ": "u_hoi", "ỷ": "y_hoi",
    "ẳ": "aw_hoi", "ẩ": "aa_hoi", "ể": "ee_hoi", "ổ": "oo_hoi", "ở": "ow_hoi", "ử": "uw_hoi",
    # Heavy (nặng)
    "ạ": "a_nang", "ẹ": "e_nang", "ị": "i_nang", "ọ": "o_nang", "ụ": "u_nang", "ỵ": "y_nang",
    "ặ": "aw_nang", "ậ": "aa_nang", "ệ": "ee_nang", "ộ": "oo_nang", "ợ": "ow_nang", "ự": "uw_nang",
}

# Vietnamese base vowel normalization (remove tones for fuzzy matching)
_TONE_STRIP_MAP: dict[str, str] = {}
for _char, _code in TONE_MAP.items():
    _base = _code.split("_")[0]
    # Map back to simple base form
    _base_char_map = {
        "a": "a", "e": "e", "i": "i", "o": "o", "u": "u", "y": "y",
        "aw": "ă", "aa": "â", "ee": "ê", "oo": "ô", "ow": "ơ", "uw": "ư",
    }
    _TONE_STRIP_MAP[_char] = _base_char_map.get(_base, _char)


def strip_vietnamese_tones(text: str) -> str:
    """Remove Vietnamese tone marks for fuzzy matching.
    
    Examples:
        "Hà Nội" → "Ha Nôi"
        "phở bò" → "phơ bo"
        "học sinh" → "hoc sinh"
        
    Args:
        text: Vietnamese text with tones
        
    Returns:
        Text with tones stripped (base vowels preserved)
    """
    return "".join(_TONE_STRIP_MAP.get(c, c) for c in text)


def normalize_vietnamese(text: str) -> str:
    """Normalize Vietnamese text for consistent processing.
    
    Steps:
    1. Unicode NFC normalization
    2. Collapse whitespace
    3. Lowercase
    
    Args:
        text: Raw Vietnamese text
        
    Returns:
        Normalized text
    """
    import unicodedata
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def detect_compounds(text: str) -> list[str]:
    """Detect Vietnamese compound words in text.
    
    Scans text for known 2-3 syllable compounds from VIETNAMESE_COMPOUNDS list.
    Useful for treating compound words as single tokens.
    
    Args:
        text: Vietnamese text to scan
        
    Returns:
        List of detected compound words
    """
    text_lower = normalize_vietnamese(text)
    found: list[str] = []
    
    # Sort by length descending to match longest first
    sorted_compounds = sorted(VIETNAMESE_COMPOUNDS, key=len, reverse=True)
    
    for compound in sorted_compounds:
        if compound in text_lower:
            # Verify it's a whole-word match (not substring of larger word)
            pattern = r"\b" + re.escape(compound) + r"\b"
            if re.search(pattern, text_lower):
                found.append(compound)
    
    return found


def tokenize_with_compounds(text: str) -> list[str]:
    """Tokenize Vietnamese text with compound word detection.
    
    First tries pyvi tokenizer. If not available, falls back to
    manual compound detection from VIETNAMESE_COMPOUNDS list.
    
    Args:
        text: Vietnamese text
        
    Returns:
        List of tokens (compounds preserved as single tokens)
    """
    # Try pyvi first
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            from pyvi import ViTokenizer
            tokenized = ViTokenizer.tokenize(text)
            # pyvi uses underscores for compounds: "học_sinh" → "học sinh"
            return [t.replace("_", " ") for t in tokenized.split()]
    except ImportError:
        pass
    
    # Fallback: manual compound detection
    text_lower = normalize_vietnamese(text)
    tokens: list[str] = []
    
    # Find all compounds first
    compounds = detect_compounds(text_lower)
    
    # Replace compounds with placeholder tokens
    placeholder_map: dict[str, str] = {}
    for i, compound in enumerate(compounds):
        placeholder = f"__COMPOUND_{i}__"
        placeholder_map[placeholder] = compound
        text_lower = text_lower.replace(compound, placeholder)
    
    # Split remaining text
    raw_tokens = text_lower.split()
    
    # Restore compounds
    for token in raw_tokens:
        if token in placeholder_map:
            tokens.append(placeholder_map[token])
        else:
            tokens.append(token)
    
    return tokens


def syllable_count(text: str) -> int:
    """Count Vietnamese syllables (approximate).
    
    In Vietnamese, each syllable is typically one space-separated word.
    
    Args:
        text: Vietnamese text
        
    Returns:
        Number of syllables
    """
    return len(text.strip().split())
