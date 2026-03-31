import asyncio
import logging
import os
import traceback
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from classifier import classify_image
from database import get_connection
from models import ImageStatus, row_to_image

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

FILTER_COLUMNS = [
    "garment_type", "style", "material", "color_palette", "pattern",
    "season", "occasion", "consumer_profile", "trend_notes",
    "location_continent", "location_country", "location_city", "designer",
]


def _classify_background(image_id: int, filepath: str, db_path: str | None = None) -> None:
    """Run classification in a background thread and save results to the DB."""
    conn = get_connection(db_path)
    try:
        conn.execute(
            "UPDATE images SET status = ? WHERE id = ?",
            (ImageStatus.PROCESSING, image_id),
        )
        conn.commit()

        result = asyncio.run(classify_image(filepath))
        desc = result.get("description")
        attrs = result.get("attributes", {})

        conn.execute(
            """UPDATE images SET
                status = ?, error_message = NULL, description = ?,
                garment_type = ?, style = ?, material = ?, color_palette = ?,
                pattern = ?, season = ?, occasion = ?, consumer_profile = ?,
                trend_notes = ?
            WHERE id = ?""",
            (
                ImageStatus.CLASSIFIED, desc,
                attrs.get("garment_type"), attrs.get("style"),
                attrs.get("material"), attrs.get("color_palette"),
                attrs.get("pattern"), attrs.get("season"),
                attrs.get("occasion"), attrs.get("consumer_profile"),
                attrs.get("trend_notes"), image_id,
            ),
        )
        conn.commit()

        conn.execute(
            """INSERT INTO images_fts
               (image_id, description, garment_type, style, material, trend_notes, annotation_text)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                str(image_id), desc or "",
                attrs.get("garment_type", ""), attrs.get("style", ""),
                attrs.get("material", ""), attrs.get("trend_notes", ""), "",
            ),
        )
        conn.commit()
        logger.info("Classified image %d", image_id)

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        logger.error("Classification failed for image %d:\n%s", image_id, traceback.format_exc())
        conn.execute(
            "UPDATE images SET status = ?, error_message = ? WHERE id = ?",
            (ImageStatus.ERROR, error_msg, image_id),
        )
        conn.commit()
    finally:
        conn.close()


@router.post("/api/images/upload", status_code=202)
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    location_continent: Optional[str] = Form(None),
    location_country: Optional[str] = Form(None),
    location_city: Optional[str] = Form(None),
    designer: Optional[str] = Form(None),
    image_year: Optional[int] = Form(None),
    image_month: Optional[int] = Form(None),
) -> dict:
    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, unique_name)

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO images (filename, filepath, original_filename,
                location_continent, location_country, location_city,
                designer, image_year, image_month, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                unique_name, filepath, file.filename,
                location_continent, location_country, location_city,
                designer, image_year, image_month, ImageStatus.PENDING,
            ),
        )
        conn.commit()
        image_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()
        result = row_to_image(row)
    finally:
        conn.close()

    background_tasks.add_task(_classify_background, image_id, filepath)
    return result


@router.get("/api/images")
async def list_images(
    garment_type: Optional[str] = None,
    style: Optional[str] = None,
    material: Optional[str] = None,
    color_palette: Optional[str] = None,
    pattern: Optional[str] = None,
    season: Optional[str] = None,
    occasion: Optional[str] = None,
    consumer_profile: Optional[str] = None,
    trend_notes: Optional[str] = None,
    location_continent: Optional[str] = None,
    location_country: Optional[str] = None,
    location_city: Optional[str] = None,
    designer: Optional[str] = None,
    image_year: Optional[int] = None,
    image_month: Optional[int] = None,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    conditions: list[str] = []
    params: list = []

    filter_map = {
        "garment_type": garment_type, "style": style, "material": material,
        "color_palette": color_palette, "pattern": pattern, "season": season,
        "occasion": occasion, "consumer_profile": consumer_profile,
        "trend_notes": trend_notes, "location_continent": location_continent,
        "location_country": location_country, "location_city": location_city,
        "designer": designer,
    }

    for col, val in filter_map.items():
        if val:
            for v in val.split(","):
                v = v.strip()
                if v:
                    conditions.append(f"INSTR(LOWER({col}), LOWER(?)) > 0")
                    params.append(v)

    if image_year is not None:
        conditions.append("image_year = ?")
        params.append(image_year)
    if image_month is not None:
        conditions.append("image_month = ?")
        params.append(image_month)

    where = " AND ".join(conditions) if conditions else "1=1"
    count_params = list(params)
    params.extend([page_size, (page - 1) * page_size])

    conn = get_connection()
    try:
        rows = conn.execute(
            f"SELECT * FROM images WHERE {where} ORDER BY uploaded_at DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) FROM images WHERE {where}", count_params
        ).fetchone()[0]
        return {
            "images": [row_to_image(r) for r in rows],
            "total": total, "page": page, "page_size": page_size,
        }
    finally:
        conn.close()


@router.get("/api/images/{image_id}")
async def get_image(image_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Image not found")
        return row_to_image(row)
    finally:
        conn.close()


@router.delete("/api/images/{image_id}")
async def delete_image(image_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Image not found")

        if os.path.exists(row["filepath"]):
            os.remove(row["filepath"])

        conn.execute("DELETE FROM images_fts WHERE image_id = ?", (str(image_id),))
        conn.execute("DELETE FROM annotations WHERE image_id = ?", (image_id,))
        conn.execute("DELETE FROM images WHERE id = ?", (image_id,))
        conn.commit()
        return {"status": "deleted"}
    finally:
        conn.close()


@router.get("/api/images/{image_id}/file")
async def get_image_file(image_id: int) -> FileResponse:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Image not found")
        if not os.path.exists(row["filepath"]):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(row["filepath"])
    finally:
        conn.close()
