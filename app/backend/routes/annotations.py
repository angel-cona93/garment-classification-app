import logging
import sqlite3

from fastapi import APIRouter, HTTPException

from database import get_connection
from models import AnnotationCreate, row_to_annotation

logger = logging.getLogger(__name__)

router = APIRouter()


def _rebuild_fts_annotations(conn: sqlite3.Connection, image_id: int) -> None:
    """Reindex annotation text in FTS after annotation changes."""
    all_anns = conn.execute(
        "SELECT tag, note FROM annotations WHERE image_id = ?", (image_id,)
    ).fetchall()
    all_text = " ".join(
        " ".join(filter(None, [a["tag"], a["note"]])) for a in all_anns
    )

    fts_row = conn.execute(
        "SELECT rowid FROM images_fts WHERE image_id = ?", (str(image_id),)
    ).fetchone()

    if fts_row:
        conn.execute(
            "UPDATE images_fts SET annotation_text = ? WHERE image_id = ?",
            (all_text, str(image_id)),
        )
    else:
        # Image may not be classified yet — create a minimal FTS entry
        img = conn.execute(
            "SELECT description, garment_type, style, material, trend_notes FROM images WHERE id = ?",
            (image_id,),
        ).fetchone()
        conn.execute(
            """INSERT INTO images_fts
               (image_id, description, garment_type, style, material, trend_notes, annotation_text)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                str(image_id),
                (img["description"] or "") if img else "",
                (img["garment_type"] or "") if img else "",
                (img["style"] or "") if img else "",
                (img["material"] or "") if img else "",
                (img["trend_notes"] or "") if img else "",
                all_text,
            ),
        )
    conn.commit()


@router.post("/api/images/{image_id}/annotations", status_code=201)
async def create_annotation(image_id: int, body: AnnotationCreate) -> dict:
    conn = get_connection()
    try:
        if not conn.execute("SELECT id FROM images WHERE id = ?", (image_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Image not found")

        cursor = conn.execute(
            "INSERT INTO annotations (image_id, tag, note) VALUES (?, ?, ?)",
            (image_id, body.tag, body.note),
        )
        conn.commit()

        _rebuild_fts_annotations(conn, image_id)

        row = conn.execute("SELECT * FROM annotations WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return row_to_annotation(row)
    finally:
        conn.close()


@router.get("/api/images/{image_id}/annotations")
async def list_annotations(image_id: int) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM annotations WHERE image_id = ? ORDER BY created_at DESC",
            (image_id,),
        ).fetchall()
        return [row_to_annotation(r) for r in rows]
    finally:
        conn.close()


@router.delete("/api/annotations/{annotation_id}")
async def delete_annotation(annotation_id: int) -> dict:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM annotations WHERE id = ?", (annotation_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Annotation not found")

        image_id = row["image_id"]
        conn.execute("DELETE FROM annotations WHERE id = ?", (annotation_id,))
        conn.commit()

        _rebuild_fts_annotations(conn, image_id)
        return {"status": "deleted"}
    finally:
        conn.close()
