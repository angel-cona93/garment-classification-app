from fastapi import APIRouter, Query

from database import get_connection
from models import row_to_image

router = APIRouter()


@router.get("/api/search")
async def search_images(q: str = Query(..., min_length=1)) -> dict:
    conn = get_connection()
    try:
        fts_rows = conn.execute(
            "SELECT image_id FROM images_fts WHERE images_fts MATCH ? ORDER BY rank",
            (q,),
        ).fetchall()
        ids = [int(r[0]) for r in fts_rows]

        if not ids:
            return {"images": [], "total": 0, "query": q}

        placeholders = ",".join(["?"] * len(ids))
        rows = conn.execute(
            f"SELECT * FROM images WHERE id IN ({placeholders}) ORDER BY uploaded_at DESC",
            ids,
        ).fetchall()
        return {"images": [row_to_image(r) for r in rows], "total": len(rows), "query": q}
    finally:
        conn.close()
