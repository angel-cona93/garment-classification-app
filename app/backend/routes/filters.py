from fastapi import APIRouter

from database import get_connection

router = APIRouter()

TEXT_FILTER_COLUMNS = [
    "garment_type", "style", "material", "color_palette", "pattern",
    "season", "occasion", "consumer_profile", "trend_notes",
    "location_continent", "location_country", "location_city", "designer",
]


@router.get("/api/filters")
async def get_filters() -> dict:
    """Return distinct values for each filterable column."""
    conn = get_connection()
    try:
        result: dict[str, list] = {}

        for col in TEXT_FILTER_COLUMNS:
            rows = conn.execute(
                f"SELECT DISTINCT {col} FROM images WHERE {col} IS NOT NULL AND {col} != ''"
            ).fetchall()
            # Split comma-separated values into individual filter options
            values: set[str] = set()
            for row in rows:
                for v in row[0].split(","):
                    v = v.strip()
                    if v:
                        values.add(v)
            result[col] = sorted(values)

        years = conn.execute(
            "SELECT DISTINCT image_year FROM images WHERE image_year IS NOT NULL ORDER BY image_year"
        ).fetchall()
        result["image_year"] = [r[0] for r in years]

        months = conn.execute(
            "SELECT DISTINCT image_month FROM images WHERE image_month IS NOT NULL ORDER BY image_month"
        ).fetchall()
        result["image_month"] = [r[0] for r in months]

        return result
    finally:
        conn.close()
