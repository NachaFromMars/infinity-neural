# Neural Memory Instinct Protocol V3
# Copy-paste vào AGENTS.md hoặc system prompt của bất kỳ AI agent nào.
# Standalone — không cần đọc SKILL.md. Đầy đủ quy tắc hành vi.

## Neural Memory Instinct Protocol (V3 — BẮT BUỘC)

> Protocol này biến nmem_* tools từ "thư viện gọi tay" thành "bản năng tự động".
> Agent đọc protocol này = biết KHI NÀO ghi, KHI NÀO tìm, tìm SÂU bao nhiêu.

---

### A. Auto-Remember — Tự Ghi

Agent PHẢI tự ghi memory khi gặp các trigger sau. KHÔNG cần user yêu cầu.

| Trigger | Category | Importance | Template |
|---------|----------|-----------|----------|
| User ra quyết định | `decision` | 7-8 | "Chọn X **vì** Y, **thay vì** Z. Ngày [date]." |
| Task hoàn thành | `workflow` | 5-6 | "Task X hoàn thành [date]. Kết quả Y. Lesson: Z." |
| User nói điều mới về bản thân | `fact` / `preference` | 5-7 | "User [thích/không thích/là/có] X." |
| Học bài học / sai lầm | `insight` / `error` | 6-8 | "Lesson: X dẫn đến Y. Fix bằng Z." |
| Quy tắc mới được lập | `instruction` | 9-10 | "Quy tắc: LUÔN/KHÔNG BAO GIỜ X." |
| Cuối session quan trọng | `context` | 3-5 | "Session [date]: làm X, kết quả Y, tiếp theo Z." |
| Info mới về project | `reference` | 5-6 | "Project X: [fact mới, metric, status]." |

**Nguyên tắc RICH CONTEXT:**
```
❌ "Dùng Opus 4.6"
✅ "Chọn Opus 4.6 vì Sonnet thiếu depth cho novel writing. Quyết định 2026-03-01, áp dụng mọi task kể cả sub-agents."
```
Càng nhiều nguyên nhân + thời gian + so sánh + lesson → recall càng chính xác.

---

### B. Auto-Recall — 3 Tầng Lazy (Giống Não Người)

**QUY TẮC SỐ 1: MỌI input phải scan Tầng 1. KHÔNG ngoại lệ.**

```
MỌI INPUT
  │
  ▼
TẦNG 1: QUICK SCAN ──── LUÔN CHẠY ────────────────── ~200 tokens
  nmem_recall(query=<keywords: danh từ riêng, tên project, concept>, depth=0)
  │
  ├─ HIT → dùng, inject vào context
  │
  ▼ MISS + mơ hồ
TẦNG 2: CONTEXT SCAN ── KHI MƠ HỒ ────────────────── ~500 tokens
  Triggers: "hồi đó", "lần trước", "cái đó", "hình như",
            "mày nói gì đó về...", hoặc CẢM THẤY nên biết
  nmem_recall(query=<semantic phrase mở rộng>, depth=2)
  │
  ├─ HIT → dùng
  │
  ▼ MISS + vẫn cảm thấy "nên biết"
TẦNG 3: DEEP SCAN ──── KHI THẬT SỰ CẦN ──────────── ~1000 tokens
  Trigger: Tầng 2 trống + topic có vẻ đã từng xuất hiện
  nmem_recall(query=<broad, nhiều keywords>, depth=3)
  │
  ├─ HIT → dùng
  │
  ▼ MISS tất cả 3 tầng
CONFIRM MỚI → thông tin mới thật sự → ghi nếu đáng (xem Auto-Remember)
```

**Tại sao Tầng 1 bắt buộc:**
- Agent có thể TƯỞNG input mới nhưng thực tế đã ghi → miss = duplicate hoặc mâu thuẫn
- Cost chỉ ~200 tokens — rẻ hơn nhiều so với hậu quả miss
- Giống não: nghe bất kỳ từ nào cũng quét xem quen không, dù chỉ 0.1 giây

---

### C. Session-Aware Loading

| Session type | Đầu session | Trong session | Cuối session |
|---|---|---|---|
| **Main** (chat trực tiếp) | `nmem_context(limit=10)` + Tầng 1 | 3 tầng đầy đủ | Auto-remember summary |
| **Sub-agent** | KHÔNG auto-load | Chỉ Tầng 1 khi keyword relevant | KHÔNG |
| **Heartbeat** | KHÔNG | KHÔNG | KHÔNG |
| **Cron job** | KHÔNG | Tầng 1 nếu cần context cũ | KHÔNG |

---

### D. Duplicate Prevention — Trước MỖI Lần Ghi

```
Muốn ghi X
  │
  ▼
nmem_recall(query=<nội dung X>, depth=0)
  │
  ├─ Tìm Y giống X (>80% trùng)
  │   ├─ Giống hoàn toàn → SKIP
  │   ├─ Gần giống + X có info mới → nmem_edit(Y)
  │   └─ X thay thế Y (fact cũ sai) → supersede Y → ghi X
  │
  └─ Không tìm thấy → nmem_remember(X)
```

---

### E. Memory Hygiene (Mỗi 3-5 Ngày)

1. `nmem_stats` — check brain health
2. Facts mâu thuẫn → supersede fact cũ
3. Hypothesis resolved → archive
4. Prediction quá deadline → verify hoặc close
5. **KHÔNG BAO GIỜ xóa cứng** trừ khi user yêu cầu hoặc security

---

### F. Chi Phí Ước Tính

| Hoạt động | Cost/lần | Tần suất |
|---|---|---|
| Tầng 1 | ~200 tokens | Mỗi message |
| Tầng 2 | ~500 tokens | ~20% messages |
| Tầng 3 | ~1000 tokens | ~5% messages |
| Remember | ~100 tokens | ~10% messages |
| Context load | ~500-1000 | 1/session |

**Trung bình:** ~300-500 tokens overhead / message. ~1.1M tokens/tháng cho 100 msg/ngày.
