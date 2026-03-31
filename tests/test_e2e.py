import sys
import os
import io
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app", "backend"))

import database
from fastapi.testclient import TestClient
from main import app
from database import init_db, get_connection


MOCK_CLASSIFICATION = {
    "description": "A beautiful flowing maxi dress in sunset orange with delicate floral embroidery along the hemline. The dress features a v-neckline and three-quarter sleeves in lightweight cotton.",
    "attributes": {
        "garment_type": "dress",
        "style": "bohemian",
        "material": "cotton",
        "color_palette": "orange, cream, green",
        "pattern": "floral",
        "season": "spring/summer",
        "occasion": "casual",
        "consumer_profile": "young professional",
        "trend_notes": "cottagecore",
    },
}


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path):
    db_path = str(tmp_path / "e2e_test.db")
    init_db(db_path)
    original = database.DB_PATH
    database.DB_PATH = db_path
    yield db_path
    database.DB_PATH = original
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def _make_test_image() -> bytes:
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), color="orange").save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def _mock_classify(image_id, filepath, db_path=None):
    """Simulate classification by writing mock results directly to DB."""
    conn = get_connection()
    try:
        desc = MOCK_CLASSIFICATION["description"]
        attrs = MOCK_CLASSIFICATION["attributes"]
        conn.execute(
            """UPDATE images SET status = 'classified', description = ?,
                garment_type = ?, style = ?, material = ?, color_palette = ?,
                pattern = ?, season = ?, occasion = ?, consumer_profile = ?,
                trend_notes = ?
            WHERE id = ?""",
            (desc, attrs["garment_type"], attrs["style"], attrs["material"],
             attrs["color_palette"], attrs["pattern"], attrs["season"],
             attrs["occasion"], attrs["consumer_profile"], attrs["trend_notes"],
             image_id),
        )
        conn.execute(
            """INSERT INTO images_fts
               (image_id, description, garment_type, style, material, trend_notes, annotation_text)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (str(image_id), desc, attrs["garment_type"], attrs["style"],
             attrs["material"], attrs["trend_notes"], ""),
        )
        conn.commit()
    finally:
        conn.close()


class TestEndToEnd:
    def test_upload_classify_filter_workflow(self, client):
        image = _make_test_image()

        with patch("routes.images._classify_background", side_effect=_mock_classify):
            resp = client.post(
                "/api/images/upload",
                files={"file": ("test_dress.jpg", image, "image/jpeg")},
                data={
                    "location_continent": "Asia", "location_country": "Japan",
                    "location_city": "Tokyo", "designer": "Test Designer",
                    "image_year": "2025", "image_month": "6",
                },
            )
            assert resp.status_code == 202
            image_id = resp.json()["id"]
            assert resp.json()["status"] == "pending"

        # Verify classification
        resp = client.get(f"/api/images/{image_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "classified"
        assert data["garment_type"] == "dress"
        assert "maxi dress" in data["description"]

        # Filter by garment type
        resp = client.get("/api/images", params={"garment_type": "dress"})
        assert resp.json()["total"] >= 1
        assert any(img["id"] == image_id for img in resp.json()["images"])

        # Filter by location
        resp = client.get("/api/images", params={"location_country": "Japan"})
        assert any(img["id"] == image_id for img in resp.json()["images"])

        # Filter by year
        resp = client.get("/api/images", params={"image_year": 2025})
        assert any(img["id"] == image_id for img in resp.json()["images"])

        # Dynamic filters include our data
        resp = client.get("/api/filters")
        filters = resp.json()
        assert "dress" in filters["garment_type"]
        assert "Japan" in filters["location_country"]

    def test_annotation_workflow(self, client):
        image = _make_test_image()

        with patch("routes.images._classify_background") as mock:
            def classify_minimal(image_id, filepath, db_path=None):
                conn = get_connection()
                try:
                    conn.execute(
                        "UPDATE images SET status = 'classified', description = 'Test' WHERE id = ?",
                        (image_id,),
                    )
                    conn.execute(
                        """INSERT INTO images_fts
                           (image_id, description, garment_type, style, material, trend_notes, annotation_text)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (str(image_id), "Test", "", "", "", "", ""),
                    )
                    conn.commit()
                finally:
                    conn.close()
            mock.side_effect = classify_minimal

            resp = client.post(
                "/api/images/upload",
                files={"file": ("test.jpg", image, "image/jpeg")},
            )
            image_id = resp.json()["id"]

        # Add annotation
        resp = client.post(
            f"/api/images/{image_id}/annotations",
            json={"tag": "inspiration", "note": "Great embroidered neckline detail"},
        )
        assert resp.status_code == 201
        assert resp.json()["tag"] == "inspiration"

        # List annotations
        resp = client.get(f"/api/images/{image_id}/annotations")
        assert len(resp.json()) == 1

        # Search by annotation text
        resp = client.get("/api/search", params={"q": "embroidered neckline"})
        assert any(img["id"] == image_id for img in resp.json()["images"])

    def test_delete_image(self, client):
        image = _make_test_image()

        with patch("routes.images._classify_background"):
            resp = client.post(
                "/api/images/upload",
                files={"file": ("test.jpg", image, "image/jpeg")},
            )
            image_id = resp.json()["id"]

        assert client.delete(f"/api/images/{image_id}").status_code == 200
        assert client.get(f"/api/images/{image_id}").status_code == 404

    def test_health_check(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
