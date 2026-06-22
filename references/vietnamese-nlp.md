# Vietnamese NLP — Bổ sung cho InfinityNeural

## Vấn đề gốc

NeuralMemory dùng English morphology expansion:
```python
_EXPANSION_SUFFIXES = ("tion", "ment", "ing", "ed", "er", "ity", "ness", ...)
_EXPANSION_PREFIXES = ("un", "re", "pre", "de", "dis")
```

Tiếng Việt = 0 hiệu quả. "Nhà giả dâm" → không match suffix/prefix nào.

## 4 Module bổ sung

### 1. Fuzzy Tone Matching (Diacritics Normalization)

Tiếng Việt có 6 thanh điệu trên mỗi nguyên âm. Khi recall, user có thể gõ sai thanh:
- "nâng" vs "nấng" vs "nắng" vs "nàng"
- "dâm" vs "dầm" vs "dám"

**Giải pháp:** Strip tones, match base vowel.

```python
_VN_TONE_MAP = {
    # a group
    'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'ắ': 'ă', 'ằ': 'ă', 'ẳ': 'ă', 'ẵ': 'ă', 'ặ': 'ă',
    'ấ': 'â', 'ầ': 'â', 'ẩ': 'â', 'ẫ': 'â', 'ậ': 'â',
    # e group
    'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ế': 'ê', 'ề': 'ê', 'ể': 'ê', 'ễ': 'ê', 'ệ': 'ê',
    # i group
    'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    # o group
    'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ố': 'ô', 'ồ': 'ô', 'ổ': 'ô', 'ỗ': 'ô', 'ộ': 'ô',
    'ớ': 'ơ', 'ờ': 'ơ', 'ở': 'ơ', 'ỡ': 'ơ', 'ợ': 'ơ',
    # u group
    'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ứ': 'ư', 'ừ': 'ư', 'ử': 'ư', 'ữ': 'ư', 'ự': 'ư',
    # y group
    'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    # d
    'đ': 'd',
}

def normalize_vietnamese(text: str) -> str:
    """Strip tones for fuzzy matching. Giữ nguyên base vowel."""
    return ''.join(_VN_TONE_MAP.get(c, c) for c in text.lower())

# Usage trong matching:
# normalize_vietnamese("nấng") == normalize_vietnamese("nắng") → True
# normalize_vietnamese("nhà giả dâm") == normalize_vietnamese("nhà giả dầm") → True
```

### 2. Vietnamese Stopwords

Loại từ vô nghĩa khỏi query để tập trung vào content words.

```python
_VN_STOPWORDS = frozenset({
    # Liên từ
    'và', 'hoặc', 'hay', 'nhưng', 'mà', 'vì', 'nếu', 'thì',
    # Giới từ
    'của', 'để', 'từ', 'trong', 'với', 'cho', 'về', 'trên', 'dưới',
    # Trợ từ
    'là', 'có', 'không', 'được', 'đã', 'sẽ', 'đang', 'cũng', 'rồi',
    # Đại từ (loại bỏ khi query, nhưng giữ khi encode)
    'tôi', 'bạn', 'anh', 'chị', 'nó', 'họ', 'chúng',
    # Lượng từ
    'các', 'những', 'một', 'nhiều', 'rất', 'tất', 'cả', 'mỗi',
    # Filler
    'ở', 'ra', 'vào', 'lên', 'xuống', 'lại', 'đi', 'đến',
    'thế', 'vậy', 'đây', 'đó', 'kia', 'này', 'nào',
})

def remove_stopwords_vi(tokens: list[str]) -> list[str]:
    """Loại Vietnamese stopwords."""
    return [t for t in tokens if t.lower() not in _VN_STOPWORDS]
```

### 3. Compound Word Detection (Basic)

Tiếng Việt hay dùng cụm từ ghép = 1 entity:
- "nhà giả dâm" = 1 concept (KHÔNG phải "nhà" + "giả" + "dâm")
- "trọng sinh" = 1 concept
- "bát nhã" = 1 concept
- "forge pipeline" = 1 concept

**Giải pháp v1:** Dictionary-based compound detection.

```python
# Compound word dictionary — mở rộng theo project
_VN_COMPOUNDS = {
    # Novel terms
    'nhà giả dâm', 'trọng sinh', 'bát nhã', 'dâm thần giả',
    'thích minh không', 'tăng nấng', 'trần nấng',
    # Tech terms
    'forge pipeline', 'sub agent', 'neural memory',
    'spreading activation', 'lateral inhibition',
    # General
    'quyết định', 'giải pháp', 'kế hoạch', 'mục tiêu',
}

def detect_compounds(text: str) -> list[str]:
    """Detect compound words, return as single tokens."""
    text_lower = text.lower()
    found = []
    for compound in sorted(_VN_COMPOUNDS, key=len, reverse=True):
        if compound in text_lower:
            found.append(compound)
            text_lower = text_lower.replace(compound, '')
    # Remaining single words
    remaining = [w for w in text_lower.split() if w.strip()]
    return found + remaining
```

### 4. Bilingual Recall (Basic)

Hỗ trợ query bằng 1 ngôn ngữ, recall từ ngôn ngữ khác.

```python
# Bilingual synonym pairs
_VN_EN_SYNONYMS = {
    'quyết định': 'decision',
    'giải pháp': 'solution',
    'vấn đề': 'problem',
    'dự án': 'project',
    'chương': 'chapter',
    'điểm số': 'score',
    'kiến trúc': 'architecture',
    'bộ nhớ': 'memory',
    'não': 'brain',
    'nén': 'compress',
}

def expand_bilingual(query_tokens: list[str]) -> list[str]:
    """Expand query with bilingual synonyms."""
    expanded = list(query_tokens)
    for token in query_tokens:
        token_lower = token.lower()
        if token_lower in _VN_EN_SYNONYMS:
            expanded.append(_VN_EN_SYNONYMS[token_lower])
        # Reverse lookup
        for vn, en in _VN_EN_SYNONYMS.items():
            if token_lower == en:
                expanded.append(vn)
    return expanded
```

## Tích hợp vào Parser

```python
# Trong extraction/parser.py, thêm vào pipeline parse query:

def parse_query(self, query: str) -> ParsedQuery:
    # 1. Detect compounds TRƯỚC khi tokenize
    compounds = detect_compounds(query)
    
    # 2. Tokenize phần còn lại
    tokens = self._tokenize(query)
    
    # 3. Remove stopwords (Vietnamese)
    tokens = remove_stopwords_vi(tokens)
    
    # 4. Expand bilingual
    tokens = expand_bilingual(tokens)
    
    # 5. Generate fuzzy variants
    fuzzy_tokens = [normalize_vietnamese(t) for t in tokens]
    
    # 6. Combine: compounds + tokens + fuzzy
    all_query_terms = compounds + tokens + fuzzy_tokens
    
    return ParsedQuery(terms=all_query_terms, ...)
```

## Giới hạn v1

- Compound detection = dictionary-based, cần bổ sung thủ công
- Bilingual chỉ ~50 pairs cơ bản
- Không có word segmentation thực sự (không dùng underthesea/vncorenlp)
- Fuzzy tone có thể false positive: "bán" ≠ "bàn" (nhưng khi recall, context phân biệt)

## Roadmap v2

- Tích hợp underthesea hoặc vncorenlp cho word segmentation
- Auto-learn compounds từ training data
- Expand bilingual dictionary tự động qua LLM
- Tone-aware scoring (exact tone > fuzzy tone)
