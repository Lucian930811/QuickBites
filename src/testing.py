import pandas as pd
from compute_content_score import content_score, only_relevant_categories, get_price_level

# ----------------------------
# Test Runner
# ----------------------------
def main():
    CSV_PATH = "../data/ca_business_enriched.csv"

    # Example "survey" inputs:
    # (Change these to test different scenarios)
    user_keywords = ["korean", "japanese"]   # cuisine keywords from survey
    user_max_price = 1                     # 1..4 ($..$$$$). Set None if user didn't answer.
    meal = "dinner"                         # "morning"/"lunch"/"dinner"/None

    df = pd.read_csv(CSV_PATH)
    df["price_level"] = df["attributes"].apply(get_price_level)

    # Optional: If you want to cut down candidates before scoring
    # (e.g., only restaurants in a city), uncomment:
    # df = df[df["city"].fillna("").str.contains("Irvine", case=False)].copy()

    # Precompute max_review_count among candidates for normalization
    max_review_count = int(df["review_count"].fillna(0).max())

    # Compute content_score for all rows
    def score_row(series_row):
        row = series_row.to_dict()
        return content_score(
            row,
            user_keywords=user_keywords,
            user_max_price=user_max_price,
            meal=meal,
            max_review_count=max_review_count
        )

    df["content_score"] = df.apply(score_row, axis=1)

    # Add readable categories
    df["matched_categories"] = df["categories"].apply(lambda s: only_relevant_categories(s, user_keywords))

    # Optionally: keep only restaurants with at least one matched category tag
    # (recommended if you want less noise)
    df_filtered = df[df["matched_categories"].fillna("").str.len() > 0].copy()

    # Sort and take top 10
    top10 = df_filtered.sort_values("content_score", ascending=False).head(10)

    # Show a compact readable output
    cols_to_show = [
        "name",
        "city",
        "state",
        "stars",
        "price_level",
        "review_count",
        "content_score",
        "matched_categories",
    ]

    # If any columns missing (rare), drop them safely
    cols_to_show = [c for c in cols_to_show if c in top10.columns]

    print("\n=== TOP 10 (by ContentScore) ===")
    print(top10[cols_to_show].to_string(index=False))


if __name__ == "__main__":
    main()