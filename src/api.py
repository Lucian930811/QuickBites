from fastapi import FastAPI
import pandas as pd
from recommender import content_score, only_relevant_categories

app = FastAPI()

df = pd.read_csv("data/ca_business_enriched.csv")
max_reviews = df["review_count"].max()

@app.get("/recommend")
def recommend(keywords: str = "", max_price: int | None = None, meal: str | None = None):
    user_keywords = [k.strip() for k in keywords.split(",") if k.strip()]

    results = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        score = content_score(
            row_dict,
            user_keywords,
            max_price,
            meal,
            max_reviews
        )

        if score > 0:
            results.append({
                "name": row_dict.get("name"),
                "stars": row_dict.get("stars"),
                "score": score,
                "matched_categories": only_relevant_categories(
                    row_dict.get("categories", ""),
                    user_keywords
                ),
                "latitude": row_dict.get("latitude"),
                "longitude": row_dict.get("longitude")
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10]
