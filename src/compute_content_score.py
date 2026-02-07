"""
QuickBites: Full end-to-end testing script (rule-based ContentScore + top-10 output
+ readable "matched_categories").

Run this file in the same environment where the CSV exists.

CSV path (as uploaded in this chat):
/mnt/data/ca_business_enriched.csv
"""

import math
import re
import json
import ast
import pandas as pd


# ----------------------------
# Helpers
# ----------------------------
def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def safe_parse_attributes(attr_str):
    """
    Your CSV 'attributes' column is a string. It often looks like a Python dict,
    but in some datasets it can be JSON-ish. We try both.
    """
    if not isinstance(attr_str, str) or not attr_str.strip():
        return {}

    s = attr_str.strip()

    # First try Python-literal dict style: "{'key': 'value', ...}"
    try:
        obj = ast.literal_eval(s)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # Then try JSON (sometimes it's valid JSON)
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # If both fail, return empty dict
    return {}


def extract_price_level_from_attributes(attr_str):
    """
    Extract Yelp-like price level from attributes:
    RestaurantsPriceRange2 is commonly 1-4.
    """
    attrs = safe_parse_attributes(attr_str)
    v = attrs.get("RestaurantsPriceRange2", None)
    if v is None:
        return None
    try:
        return int(v)
    except Exception:
        # sometimes it is "2.0" or something odd
        try:
            return int(float(v))
        except Exception:
            return None

def get_price_level(attr_str):
    attrs = safe_parse_attributes(attr_str)
    v = attrs.get("RestaurantsPriceRange2")
    if v is None:
        return None
    try:
        return int(v)
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return None


def tokenize_categories(categories_str):
    if not isinstance(categories_str, str) or not categories_str.strip():
        return []
    return [c.strip() for c in categories_str.split(",") if c.strip()]


def cuisine_match(user_keywords, categories_str):
    """
    Returns 0..1
    - 1.0 if any keyword appears in categories (whole-word-ish)
    - 0.5 if user didn't specify anything (neutral)
    - 0.0 otherwise
    """
    if not user_keywords:
        return 0.5

    cats = " ".join(tokenize_categories(categories_str)).lower()
    for k in user_keywords:
        k = (k or "").strip().lower()
        if not k:
            continue
        if re.search(rf"\b{re.escape(k)}\b", cats):
            return 1.0
    return 0.0


def price_match(user_max_price, rest_price_level):
    """
    Returns 0..1
    If user didn't specify budget -> neutral 0.5
    If restaurant missing price -> neutral 0.5
    Else:
      <= budget -> 1.0
      == budget+1 -> 0.5
      else -> 0.0
    """
    if user_max_price is None:
        return 0.5
    if rest_price_level is None:
        return 0.5

    if rest_price_level <= user_max_price:
        return 1.0
    if rest_price_level == user_max_price + 1:
        return 0.5
    return 0.0


def quality_score(stars, review_count, max_review_count):
    """
    stars: 0..5
    review_count: skewed -> log normalize within candidate set
    """
    stars = 0.0 if pd.isna(stars) else float(stars)
    review_count = 0 if pd.isna(review_count) else int(review_count)

    stars_norm = clamp01(stars / 5.0)

    denom = math.log1p(max(1, int(max_review_count)))
    review_norm = math.log1p(max(0, review_count)) / denom

    return clamp01(0.6 * stars_norm + 0.4 * review_norm)


def sentiment_score(sent_pos_mean, sent_neg_mean):
    """
    net = pos - neg, map roughly [-1,1] -> [0,1]
    If values are missing, defaults to 0.5-ish behavior via zeros.
    """
    pos = 0.0 if pd.isna(sent_pos_mean) else float(sent_pos_mean)
    neg = 0.0 if pd.isna(sent_neg_mean) else float(sent_neg_mean)

    net = pos - neg
    return clamp01((net + 1.0) / 2.0)


def mealtime_fit(meal, row_dict):
    """
    meal in {"morning","lunch","dinner"} or None
    Uses morning_rate/lunch_rate/dinner_rate columns.
    """
    def get_rate(k):
        v = row_dict.get(k, 0.0)
        return 0.0 if pd.isna(v) else float(v)

    m = clamp01(get_rate("morning_rate"))
    l = clamp01(get_rate("lunch_rate"))
    d = clamp01(get_rate("dinner_rate"))

    if meal == "morning":
        return m
    if meal == "lunch":
        return l
    if meal == "dinner":
        return d
    return (m + l + d) / 3.0


def content_score(row_dict, user_keywords=None, user_max_price=None, meal=None, max_review_count=1000):
    """
    ContentScore = intent match + quality + sentiment + mealtime + open bonus
    Returns 0..1
    """
    cm = cuisine_match(user_keywords, row_dict.get("categories", ""))

    rest_price_level = extract_price_level_from_attributes(row_dict.get("attributes", ""))
    pm = price_match(user_max_price, rest_price_level)

    q = quality_score(row_dict.get("stars", 0.0), row_dict.get("review_count", 0), max_review_count)

    s = sentiment_score(row_dict.get("sent_pos_mean", 0.0), row_dict.get("sent_neg_mean", 0.0))

    mt = mealtime_fit(meal, row_dict)

    # is_open in your CSV is a business-level flag, not necessarily "open right now"
    is_open_val = row_dict.get("is_open", 0)
    try:
        openbiz = 1.0 if int(is_open_val) == 1 else 0.0
    except Exception:
        openbiz = 0.0

    # Weights (sum to 1.0)
    score = (
        0.30 * cm +
        0.20 * pm +
        0.20 * q +
        0.15 * s +
        0.10 * mt +
        0.05 * openbiz
    )
    return clamp01(score)


def only_relevant_categories(categories_str, keywords):
    """
    For readability: only keep category tags that match user's keywords.
    Example: keywords ["ramen","japanese"] -> keep tags that contain those.
    """
    if not keywords:
        return categories_str if isinstance(categories_str, str) else ""

    cats = tokenize_categories(categories_str)
    out = []
    for c in cats:
        c_low = c.lower()
        if any(re.search(rf"\b{re.escape((k or '').strip().lower())}\b", c_low) for k in keywords if k):
            out.append(c)
    return ", ".join(out)


