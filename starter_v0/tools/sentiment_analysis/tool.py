from __future__ import annotations

from typing import Any

from tools._shared import err, fold_text
from tools.social_search.tool import search_tweets


POSITIVE_TERMS = {
    "hay",
    "rat hay",
    "xuat sac",
    "dinh",
    "cuon",
    "thich",
    "yeu thich",
    "tuyet voi",
    "amazing",
    "great",
    "excellent",
    "love",
    "fire",
    "banger",
    "masterpiece",
}

NEGATIVE_TERMS = {
    "do",
    "te",
    "chan",
    "that vong",
    "khong hay",
    "nham chan",
    "toi",
    "kem",
    "bad",
    "awful",
    "terrible",
    "boring",
    "hate",
    "worst",
    "mid",
}

POSITIVE_HINTS = {"😍", "❤️", "🔥", "👏", "👍", "love", "best", "hay", "dinh", "xuat sac"}
NEGATIVE_HINTS = {"😡", "🤮", "👎", "hate", "bad", "boring", "te", "that vong", "kem"}


def _label_from_score(score: int) -> str:
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"


def _score_text(text: str) -> int:
    folded = fold_text(text)
    score = 0
    for term in POSITIVE_TERMS:
        if term in folded:
            score += 1
    for term in NEGATIVE_TERMS:
        if term in folded:
            score -= 1
    for hint in POSITIVE_HINTS:
        if hint in folded or hint in text:
            score += 1
    for hint in NEGATIVE_HINTS:
        if hint in folded or hint in text:
            score -= 1
    return score


def analyze_social_sentiment(query: str = "", limit: int = 20, search_type: str = "Latest") -> dict[str, Any]:
    """
    Analyze sentiment of recent social posts for a topic.
    """
    try:
        limit = max(5, min(int(limit or 20), 50))
        search = search_tweets(query=query, search_type=search_type, limit=limit)
        items = search.get("items", []) if isinstance(search, dict) else []

        sentiment_items: list[dict[str, Any]] = []
        counts = {"positive": 0, "neutral": 0, "negative": 0}

        for item in items:
            text = (item.get("summary") or item.get("title") or "").strip()
            score = _score_text(text)
            label = _label_from_score(score)
            counts[label] += 1
            sentiment_items.append(
                {
                    "label": label,
                    "score": score,
                    "title": item.get("title", ""),
                    "source": item.get("source", ""),
                    "url": item.get("url", ""),
                    "date": item.get("date", ""),
                }
            )

        total = max(len(sentiment_items), 1)
        avg_score = round(sum(x["score"] for x in sentiment_items) / total, 3)
        overall = _label_from_score(1 if avg_score > 0.1 else (-1 if avg_score < -0.1 else 0))

        return {
            "tool": "analyze_social_sentiment",
            "query": query,
            "search_type": search_type,
            "sample_size": len(sentiment_items),
            "overall_sentiment": overall,
            "average_score": avg_score,
            "distribution": {
                "positive": counts["positive"],
                "neutral": counts["neutral"],
                "negative": counts["negative"],
                "positive_ratio": round(counts["positive"] / total, 3),
                "neutral_ratio": round(counts["neutral"] / total, 3),
                "negative_ratio": round(counts["negative"] / total, 3),
            },
            "items": sentiment_items,
            "note": (
                "Heuristic sentiment from keyword/emoji signals on recent social posts. "
                "Use as directional signal, not ground truth."
            ),
        }
    except Exception as exc:
        return err("analyze_social_sentiment", exc)
