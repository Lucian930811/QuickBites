from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel
import ast
import json
from compute_content_score import content_score, only_relevant_categories

app = FastAPI()

# If running from inside the `src` folder, the data is up one level
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "../data/ca_business_enriched.csv")

df = pd.read_csv(csv_path)

def safe_float(val):
    if val is None:
        return None
    try:
        import math
        f = float(val)
        if math.isnan(f):
            return None
        return f
    except (ValueError, TypeError):
        return None

max_reviews = df["review_count"].max()

# --- User Profile & Memory Setup ---
PROFILE_FILE = os.path.join(base_dir, "../data/test_user_profile.json")

def load_profile():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # Initialize default profile structure
    return {
        "user_id": "test_user_001",
        "long_term": {
            "cuisine": {},      # e.g., "ramen": 5.0
            "price_level": {}   # e.g., "1": 3.0
        },
        "short_term": []        # List of recent interaction dicts
    }

def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=2)

user_profile = load_profile()

EVENT_WEIGHTS = {
    "click": 1.0,
    "details_view": 2.0,
    "save": 5.0,
    "route_started": 10.0,
    "skip": -1.0
}
MAX_SHORT_TERM_EVENTS = 20

class InteractionEvent(BaseModel):
    business_id: str
    event_type: str
    categories: str | None = None
    price_level: int | None = None

@app.post("/interact")
def log_interaction(event: InteractionEvent):
    global user_profile
    weight = EVENT_WEIGHTS.get(event.event_type, 0.0)
    
    if weight == 0:
        return {"status": "ignored", "reason": "unknown event type"}

    # Update Long-term memory
    # 1. Cuisine preferences
    if event.categories:
        from compute_content_score import tokenize_categories
        cats = tokenize_categories(event.categories)
        for c in cats:
            c = c.lower()
            user_profile["long_term"]["cuisine"][c] = user_profile["long_term"]["cuisine"].get(c, 0.0) + weight
            
    # 2. Price preferences
    if event.price_level is not None:
        p_str = str(event.price_level)
        user_profile["long_term"]["price_level"][p_str] = user_profile["long_term"]["price_level"].get(p_str, 0.0) + weight

    # Update Short-term memory
    # Add to the front of the list, keep only latest MAX_SHORT_TERM_EVENTS
    interaction_record = {
        "business_id": event.business_id,
        "event_type": event.event_type,
        "weight": weight,
        "categories": event.categories,
        "price_level": event.price_level
    }
    user_profile["short_term"].insert(0, interaction_record)
    user_profile["short_term"] = user_profile["short_term"][:MAX_SHORT_TERM_EVENTS]

    save_profile(user_profile)
    return {"status": "success", "profile": user_profile}


@app.get("/recommend")
def recommend(keywords: str = "", max_price: int | None = None, meal: str | None = None, personalize: bool = False):
    user_keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    results = []

    profile_to_use = user_profile if personalize else None

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        # score can be 0 if you want to include all
        score, explanation = content_score(row_dict, user_keywords, max_price, meal, max_reviews, profile_to_use)

        # parse attributes safely
        attributes_raw = row_dict.get("attributes")
        price_level_int = None
        good_for_meal = None
        if isinstance(attributes_raw, str):
            try:
                attributes = ast.literal_eval(attributes_raw)
                price_raw = attributes.get("RestaurantsPriceRange2")
                good_for_meal = attributes.get("GoodForMeal")
                try:
                    price_level_int = int(price_raw)
                except (TypeError, ValueError):
                    price_level_int = None
            except Exception:
                pass  # just skip parsing attributes if it fails

        results.append({
            "business_id": row_dict.get("business_id"),
            "name": row_dict.get("name"),
            "stars": safe_float(row_dict.get("stars")),
            "review_count": row_dict.get("review_count") if not pd.isna(row_dict.get("review_count")) else None,
            "score": safe_float(score),
            "explanation": explanation,
            "matched_categories": only_relevant_categories(
                row_dict.get("categories", ""),
                user_keywords
            ),
            "latitude": safe_float(row_dict.get("latitude")),
            "longitude": safe_float(row_dict.get("longitude")),
            "address": row_dict.get("address") if not pd.isna(row_dict.get("address")) else None,
            "city": row_dict.get("city") if not pd.isna(row_dict.get("city")) else None,
            "state": row_dict.get("state") if not pd.isna(row_dict.get("state")) else None,
            "hours": row_dict.get("hours") if not pd.isna(row_dict.get("hours")) else None,
            "price_level": price_level_int,
            "is_vegan": "Vegan" in (str(row_dict.get("categories")) or ""),
            "good_for_meal": str(good_for_meal) if good_for_meal else None
        })


    # sort top 10
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10]

@app.get("/profile")
def get_profile():
    return user_profile

@app.delete("/profile")
def reset_profile():
    global user_profile
    if os.path.exists(PROFILE_FILE):
        os.remove(PROFILE_FILE)
    user_profile = load_profile()
    return {"status": "success", "message": "Profile reset to default"}



class Preferences(BaseModel):
    max_price: int | None = None
    meal: str | None = None
    personalize: bool = False

class SearchRequest(BaseModel):
    query: str
    preferences: Preferences

@app.post("/search")
def search(req: SearchRequest):
    keywords = [k.strip() for k in req.query.split(",") if k.strip()]
    
    profile_to_use = user_profile if req.preferences.personalize else None

    results = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        score, explanation = content_score(
            row_dict,
            keywords,
            req.preferences.max_price,
            req.preferences.meal,
            max_reviews,
            profile_to_use
        )

        if score > 0:
            categories = row_dict.get("categories") or ""
            raw_attributes = row_dict.get("attributes")
            attributes = {}

            if raw_attributes:
                try:
                    attributes = ast.literal_eval(raw_attributes)
                except:
                    attributes = {}

            price_level_int = None
            good_for_meal = None

            try:
                price_level_int = int(attributes.get("RestaurantsPriceRange2"))
            except (TypeError, ValueError):
                price_level_int = None

            good_for_meal = attributes.get("GoodForMeal")

            results.append({
                "business_id": row_dict.get("business_id"),
                "name": row_dict.get("name"),
                "stars": safe_float(row_dict.get("stars")),
                "review_count": row_dict.get("review_count") if not pd.isna(row_dict.get("review_count")) else None,
                "score": safe_float(score),
                "explanation": explanation,
                "matched_categories": only_relevant_categories(categories, keywords),
                "latitude": safe_float(row_dict.get("latitude")),
                "longitude": safe_float(row_dict.get("longitude")),
                "price_level": price_level_int,
                "address": row_dict.get("address") if not pd.isna(row_dict.get("address")) else None,
                "city": row_dict.get("city") if not pd.isna(row_dict.get("city")) else None,
                "state": row_dict.get("state") if not pd.isna(row_dict.get("state")) else None,
                "hours": row_dict.get("hours") if not pd.isna(row_dict.get("hours")) else None,
                "is_vegan": "Vegan" in str(categories),
                "good_for_meal": good_for_meal or {}
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10]
