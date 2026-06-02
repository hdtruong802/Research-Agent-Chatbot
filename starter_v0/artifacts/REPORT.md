# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: 2 zone 8
- Members: Truong, Linh, Ha
- Provider/model: OpenRouter / openai/gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent cho bài toán theo dõi thông tin: tìm bài đăng theo tài khoản/chủ đề, tra web news, đọc URL cụ thể, phân tích sentiment mạng xã hội, format digest, và hỗ trợ gửi Telegram có bước xác nhận.
Agent hỗ trợ cả single-turn và multi-turn (carry context, sửa yêu cầu theo turn mới nhất, và hỏi lại bằng `clarify` khi thiếu dữ liệu bắt buộc).

**Link dùng thử (deploy):**

> URL: Local Streamlit app (run `streamlit run starter_v0/streamlit_app.py`). Public URL: (update if deployed)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | lấy tweet gần đây của một tài khoản X cụ thể | không |
| social_search | tìm tweet theo chủ đề/từ khóa (Latest/Top) | không |
| lookup | tìm thông tin trên web, đặc biệt news theo timeframe | không |
| fetch | đọc/tóm tắt nội dung từ URL cụ thể | không |
| format | render dữ liệu thành digest markdown | không |
| send | gửi nội dung lên Telegram (có cơ chế xác nhận) | không |
| policy | tìm kiếm trong tài liệu policy nội bộ | không |
| papers | tìm paper trên arXiv theo chủ đề | không |
| paper_text | lấy text từ paper arXiv | không |
| sentiment_analysis | phân tích sắc thái social theo chủ đề (positive/neutral/negative) | có |

## A3. Câu hỏi mẫu để thử

1. Tweet mới nhất nói về ông chú Chum là gì?
2. Tin tức AI hôm nay có gì nổi bật? (chỉ lấy web news)
3. Tóm tắt bài này giúp mình: https://openai.com/index/introducing-gpt-4-1/
4. Mọi người có thái độ như thế nào đối với bài hát mới của Sơn Tùng MTP? (phân tích sắc thái social)
5. Đăng bản tin này lên Telegram giúp mình. (kiểm tra agent có hỏi xác nhận trước khi gửi)

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
