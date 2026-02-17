from fastapi import FastAPI
import pandas as pd
from pydantic import BaseModel
import ast
from compute_content_score import content_score, only_relevant_categories

app = FastAPI()

df = pd.read_csv("data/ca_business_enriched.csv")
max_reviews = df["review_count"].max()

@app.get("/recommend")
def recommend(keywords: str = "", max_price: int | None = None, meal: str | None = None):
    user_keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    results = []

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        # score can be 0 if you want to include all
        score = content_score(row_dict, user_keywords, max_price, meal, max_reviews)

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
            "stars": row_dict.get("stars"),
            "review_count": row_dict.get("review_count"),
            "score": score,
            "matched_categories": only_relevant_categories(
                row_dict.get("categories", ""),
                user_keywords
            ),
            "latitude": row_dict.get("latitude"),
            "longitude": row_dict.get("longitude"),
            "address": row_dict.get("address"),
            "city": row_dict.get("city"),
            "state": row_dict.get("state"),
            "hours": row_dict.get("hours"),
            "price_level": price_level_int,
            "is_vegan": "Vegan" in (row_dict.get("categories") or ""),
            "good_for_meal": str(good_for_meal) if good_for_meal else None
        })

    # sort top 10
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10]


class Preferences(BaseModel):
    max_price: int | None = None
    meal: str | None = None

class SearchRequest(BaseModel):
    query: str
    preferences: Preferences

@app.post("/search")
def search(req: SearchRequest):
    keywords = [k.strip() for k in req.query.split(",") if k.strip()]

    results = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        score = content_score(
            row_dict,
            keywords,
            req.preferences.max_price,
            req.preferences.meal,
            max_reviews
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
                "stars": row_dict.get("stars"),
                "review_count": row_dict.get("review_count"),
                "score": score,
                "matched_categories": only_relevant_categories(categories, keywords),
                "latitude": row_dict.get("latitude"),
                "longitude": row_dict.get("longitude"),
                "price_level": price_level_int,
                "address": row_dict.get("address"),
                "city": row_dict.get("city"),
                "state": row_dict.get("state"),
                "hours": row_dict.get("hours"),
                "is_vegan": "Vegan" in categories,
                "good_for_meal": good_for_meal or {}
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10]
