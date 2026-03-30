"""
sentiment_service.py
====================
Real NLP-based sentiment scoring using TextBlob.
Falls back to keyword scoring if TextBlob unavailable.

score_news(headlines: list[str]) -> dict
  Returns: sentiment_score (-1 to +1), label, confidence, details
"""

import re

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

# Extended financial keyword lexicon
POSITIVE_WORDS = {
    "profit", "growth", "gain", "surge", "rally", "bullish", "strong",
    "beat", "record", "upgrade", "outperform", "buy", "upside", "boost",
    "revenue", "expansion", "positive", "rise", "jump", "soar", "climb",
    "earnings", "dividend", "acquisition", "deal", "order", "contract",
    "recovery", "improve", "milestone", "exceed", "breakthrough"
}

NEGATIVE_WORDS = {
    "loss", "fall", "drop", "decline", "bearish", "weak", "miss",
    "downgrade", "underperform", "sell", "downside", "cut", "crash",
    "debt", "risk", "concern", "negative", "slump", "plunge", "tumble",
    "fraud", "investigation", "penalty", "fine", "lawsuit", "default",
    "layoff", "recession", "inflation", "warning", "disappoint", "delay"
}


def _keyword_score(text: str) -> float:
    """Returns -1 to +1 based on keyword matching."""
    words = set(re.findall(r'\b\w+\b', text.lower()))
    pos = len(words & POSITIVE_WORDS)
    neg = len(words & NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        return 0.0
    return round((pos - neg) / total, 3)


def score_news(headlines: list) -> dict:
    """
    Accepts a list of headline strings.
    Returns dict with overall sentiment and per-headline breakdown.
    """
    if not headlines:
        return {
            "sentiment_score": 0.0,
            "label": "NEUTRAL",
            "confidence": 0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "details": []
        }

    details   = []
    scores    = []
    pos_count = 0
    neg_count = 0
    neu_count = 0

    for h in headlines:
        text = str(h).strip()
        if not text:
            continue

        if TEXTBLOB_AVAILABLE:
            blob      = TextBlob(text)
            polarity  = round(blob.sentiment.polarity, 3)
            subjectivity = round(blob.sentiment.subjectivity, 3)
        else:
            polarity     = _keyword_score(text)
            subjectivity = 0.5

        # Blend TextBlob polarity with keyword boost
        kw_score = _keyword_score(text)
        blended  = round(0.6 * polarity + 0.4 * kw_score, 3)

        if blended > 0.05:
            label = "POSITIVE"
            pos_count += 1
        elif blended < -0.05:
            label = "NEGATIVE"
            neg_count += 1
        else:
            label = "NEUTRAL"
            neu_count += 1

        scores.append(blended)
        details.append({
            "headline":    text[:120],
            "score":       blended,
            "label":       label,
            "subjectivity": subjectivity
        })

    if not scores:
        avg_score = 0.0
    else:
        # Weighted average — give more weight to extreme scores
        avg_score = round(sum(scores) / len(scores), 3)

    confidence = round(abs(avg_score) * 100, 1)

    if avg_score >= 0.15:
        overall_label = "POSITIVE"
    elif avg_score <= -0.15:
        overall_label = "NEGATIVE"
    else:
        overall_label = "NEUTRAL"

    return {
        "sentiment_score":  avg_score,
        "label":            overall_label,
        "confidence":       confidence,
        "positive_count":   pos_count,
        "negative_count":   neg_count,
        "neutral_count":    neu_count,
        "details":          details
    }
