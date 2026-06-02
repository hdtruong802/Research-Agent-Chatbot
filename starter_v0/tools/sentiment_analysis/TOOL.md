---
name: sentiment_analysis
track: bonus
kind: live_api
provider: RapidAPI Twitter API45 (via social_search)
requires_env: [RAPIDAPI_KEY, RAPIDAPI_TWITTER_HOST]
inputs: [query, limit, search_type]
outputs: [overall_sentiment, average_score, distribution, items]
side_effect: false
---
# sentiment_analysis

Analyzes recent social posts for a topic and returns overall sentiment
(`positive`, `neutral`, `negative`) with distribution and scored samples.

Recommended for questions like:
- "Mọi người có thái độ như thế nào đối với bài hát mới của Sơn Tùng MTP?"
