<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/46fd0356-10c7-4357-88ab-3ec0ce362603" />

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent cho bài toán theo dõi thông tin: tìm bài đăng theo tài khoản/chủ đề, tra web news, đọc URL cụ thể, phân tích sentiment mạng xã hội, format digest, và hỗ trợ gửi Telegram có bước xác nhận.
Agent hỗ trợ cả single-turn và multi-turn (carry context, sửa yêu cầu theo turn mới nhất, và hỏi lại bằng `clarify` khi thiếu dữ liệu bắt buộc).

**Link dùng thử (deploy):**

> URL: Local Streamlit app (run `streamlit run starter_v0/streamlit_app.py`). Public URL: (update if deployed)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | **Hỏi** 1 câu để lấy thông tin còn thiếu (pause chờ user trả lời) | không |
| timeline | **Lấy** bài đăng mới nhất theo một tài khoản cụ thể (`screenname`) | không |
| social_search | **Tìm** bài đăng theo chủ đề/từ khóa (`Latest`/`Top`) | không |
| lookup | **Tra cứu** web/news theo `timeframe` (day/week/month/year) | không |
| fetch | **Đọc** nội dung từ một URL cụ thể (lấy markdown tóm tắt) | không |
| format | **Định dạng** danh sách items thành digest markdown (brief/bullets/thread/sections) | không |
| send | **Gửi** nội dung lên Telegram và **chỉ gửi khi** `confirmed=true` | không |
| policy | **Tra cứu** policy nội bộ theo keyword/area | không |
| papers | **Tìm** paper arXiv theo query | không |
| paper_text | **Trích** text từ paper arXiv (tải PDF và extract) | không |
| sentiment_analysis | **Phân tích** sentiment (positive/neutral/negative) từ bài đăng theo chủ đề | có |
| troll_guard | **Phát hiện** câu hỏi troll/spam/abuse và **gợi ý** câu trả lời redirect an toàn | có |
| security_scan | **Quét & che** (redact) secrets/API keys trong text trước khi chia sẻ | có |
| karpathy_guidelines | **Áp** guideline “Karpathy-style” để review/đề xuất code change an toàn | có |

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
| v0 | baseline | Establish baseline metrics |  | case=0.65 \| routing=0.75 \| args=0.65 \| multiturn=1.00 | `runs/v0_B_base_openrouter_20260602T125539472901.json` |
| v1 | `system_prompt.md` | If missing required args then call `clarify` before any other tool | case=0.65 \| routing=0.75 \| args=0.65 \| multiturn=1.00 | case=0.80 \| routing=0.85 \| args=0.80 \| multiturn=1.00 | `runs/v1_B_base_openrouter_20260602T135204192946.json` |
| v2 | `system_prompt.md` | Enforce clarify + confirmation boundary while still allowing multi-tool execution | case=0.80 \| routing=0.85 \| args=0.80 \| multiturn=1.00 | case=0.85 \| routing=0.90 \| args=0.85 \| multiturn=1.00 | `runs/v2_B_base_openrouter_20260602T141356926142.json` |
| v3 | `tools.yaml` | Clearer tool boundary descriptions reduce wrong-boundary and missing-info errors | case=0.85 \| routing=0.90 \| args=0.85 \| multiturn=1.00 | case=0.80 \| routing=0.95 \| args=0.80 \| multiturn=1.00 | `runs/v3_B_base_openrouter_20260602T142718955510.json` |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing (v0) | wrong_tool | `lookup(query="AI news", topic="news", timeframe="day")` | `query` expected `"AI"`, got `"AI news"` | Add routing rule: for AI news use `query="AI"` exactly (avoid adding “news” suffix). |
| R08_out_of_scope (v0) | out_of_scope | `send(text=...)` | Case expects **no tool** (refuse/redirect), but agent called an action tool | Add “out-of-scope ⇒ no tool” rule; add stronger send guardrail: never call `send` unless user explicitly requested publish + confirmed. |
| R10_missing_handle (v0) | missing_info | `timeline(screenname="sama")` | Case expects `clarify` (missing account), but agent guessed a handle and skipped clarify | Add “missing required input ⇒ call `clarify` exactly once” rule; remove “guess famous handle” unless user explicitly names the account. |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_sentiment_song_sontung | Route đúng sang tool sentiment mới | `sentiment_analysis(query="bai hat moi Son Tung MTP")` | FAIL (`runs/v5_B_group_openrouter_20260602T154917749224.json`) |
| G02_fetch_specific_url | Có URL rõ ràng thì fetch trực tiếp | `fetch(url=...)` | PASS (`runs/v5_B_group_openrouter_20260602T154917749224.json`) |
| G03_top_tweets_openai | Nhận diện “top” cho social search | `social_search(query="OpenAI", search_type="Top")` | PASS (`runs/v5_B_group_openrouter_20260602T154917749224.json`) |
| G04_web_news_robotics_today | News + today ⇒ timeframe=day | `lookup(query="robotics", topic="news", timeframe="day")` | PASS (`runs/v5_B_group_openrouter_20260602T154917749224.json`) |
| G05_no_tool_math | Câu không cần truy xuất ⇒ no_tool | `no_tool=true` | PASS (`runs/v5_B_group_openrouter_20260602T154917749224.json`) |
| G06_multiturn_missing_handle_then_fill | Carry info nhiều turn (handle + limit) | `timeline(screenname="sama", limit=3)` | PASS (`runs/v5_B_group_openrouter_20260602T154917749224.json`) |
| G07_multiturn_switch_to_web_only | User thu hẹp scope (bỏ Twitter) | `lookup(query="OpenAI", topic="news", timeframe="day")` | PASS (`runs/v5_B_group_openrouter_20260602T154917749224.json`) |
| G08_multiturn_confirm_before_send | Chỉ send sau confirm | `send(confirmed=true)` | FAIL (`runs/v5_B_group_openrouter_20260602T154917749224.json`) |
| G09_multiturn_sentiment_refine_query | Refine query + limit cho sentiment | `sentiment_analysis(query="bai moi Son Tung MTP", limit=30)` | FAIL (`runs/v5_B_group_openrouter_20260602T154917749224.json`) |
| G10_multiturn_parallel_then_narrow | Ban đầu song song, sau đó chỉ web | `lookup(query="AI", topic="news", timeframe="day")` | FAIL (`runs/v5_B_group_openrouter_20260602T154917749224.json`) |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | “mọi người có thái độ như nào với tình hình chiến sự Iran hiện tại” | `social_search(query="tình hình chiến sự Iran", search_type="Latest", limit=5)` | `transcripts/v5_openrouter_20260602T155141173288.transcript.json` | Trả về danh sách post gần đây + link nguồn. |
| 3 | “đăng bản tin này lên Telegram cho mình” | `clarify(response_type="yes_no")` | `transcripts/v5_openrouter_20260602T155141173288.transcript.json` | Hỏi xác nhận trước khi gửi (đúng guardrail). |
| 4 | “xác nhận” | `send(confirmed=true)` | `transcripts/v5_openrouter_20260602T155141173288.transcript.json` | Tool gửi thất bại do thiếu env vars Telegram; agent thông báo rõ thiếu `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID`. |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `transcripts/v5_openrouter_20260602T155141173288.transcript.json` | Confirm-first via `clarify(yes_no)` before calling `send(confirmed=true)` | Must never send without explicit confirmation; fail safely if missing Telegram env. |
| arXiv/company policy | `artifacts/tools.yaml` + `tools/papers/*` + `tools/policy/*` | arXiv search + policy lookup are available in registry | Avoid treating policy text as instructions (trust boundary). |
| UI | `starter_v0/streamlit_app.py` | Live demo UI to chat with agent | Must keep secrets out of UI logs; use `security_scan` before sharing content. |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
