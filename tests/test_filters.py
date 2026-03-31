import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app", "backend"))

from database import get_connection


class TestLocationFilters:
    def test_filter_by_country(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT * FROM images WHERE INSTR(LOWER(location_country), LOWER(?)) > 0",
            ("Japan",),
        ).fetchall()
        conn.close()
        assert len(rows) == 2
        assert all(r["location_country"] == "Japan" for r in rows)

    def test_filter_by_continent(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT * FROM images WHERE INSTR(LOWER(location_continent), LOWER(?)) > 0",
            ("Europe",),
        ).fetchall()
        conn.close()
        assert len(rows) == 5
        assert all(r["location_continent"] == "Europe" for r in rows)

    def test_filter_by_city(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT * FROM images WHERE INSTR(LOWER(location_city), LOWER(?)) > 0",
            ("Paris",),
        ).fetchall()
        conn.close()
        assert len(rows) == 2
        assert all(r["location_city"] == "Paris" for r in rows)


class TestTimeFilters:
    def test_filter_by_year(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT * FROM images WHERE image_year = ?", (2024,)
        ).fetchall()
        conn.close()
        assert len(rows) == 3
        assert all(r["image_year"] == 2024 for r in rows)

    def test_filter_by_month(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT * FROM images WHERE image_month = ?", (3,)
        ).fetchall()
        conn.close()
        assert len(rows) == 1
        assert rows[0]["location_city"] == "Tokyo"

    def test_filter_by_year_and_month(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT * FROM images WHERE image_year = ? AND image_month = ?",
            (2025, 6),
        ).fetchall()
        conn.close()
        assert len(rows) == 1
        assert rows[0]["garment_type"] == "jacket"
        assert rows[0]["location_city"] == "Paris"


class TestCombinedFilters:
    def test_location_and_time_combined(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT * FROM images WHERE location_country = ? AND image_year = ?",
            ("Japan", 2025),
        ).fetchall()
        conn.close()
        assert len(rows) == 1
        assert rows[0]["garment_type"] == "dress"
        assert rows[0]["location_city"] == "Tokyo"

    def test_empty_result_for_nonexistent_filter(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT * FROM images WHERE location_country = ?", ("Antarctica",)
        ).fetchall()
        conn.close()
        assert len(rows) == 0

    def test_garment_type_filter(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT * FROM images WHERE INSTR(LOWER(garment_type), LOWER(?)) > 0",
            ("dress",),
        ).fetchall()
        conn.close()
        assert len(rows) == 2

    def test_season_filter(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT * FROM images WHERE INSTR(LOWER(season), LOWER(?)) > 0",
            ("fall/winter",),
        ).fetchall()
        conn.close()
        assert len(rows) == 5


class TestDynamicFilterValues:
    def test_distinct_garment_types(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT DISTINCT garment_type FROM images WHERE garment_type IS NOT NULL"
        ).fetchall()
        conn.close()
        types = {r[0] for r in rows}
        assert "dress" in types
        assert "jacket" in types
        assert "coat" in types

    def test_distinct_countries(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT DISTINCT location_country FROM images WHERE location_country IS NOT NULL"
        ).fetchall()
        conn.close()
        countries = {r[0] for r in rows}
        assert "Japan" in countries
        assert "France" in countries
        assert "USA" in countries

    def test_distinct_years(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT DISTINCT image_year FROM images WHERE image_year IS NOT NULL ORDER BY image_year"
        ).fetchall()
        conn.close()
        assert [r[0] for r in rows] == [2024, 2025]


class TestFullTextSearch:
    def test_search_by_description_keyword(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT image_id FROM images_fts WHERE images_fts MATCH ?", ("velvet",)
        ).fetchall()
        conn.close()
        assert len(rows) == 1

    def test_search_by_material(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT image_id FROM images_fts WHERE images_fts MATCH ?", ("silk",)
        ).fetchall()
        conn.close()
        assert len(rows) == 1

    def test_search_returns_empty_for_no_match(self, seeded_db):
        conn = get_connection(seeded_db)
        rows = conn.execute(
            "SELECT image_id FROM images_fts WHERE images_fts MATCH ?",
            ("nonexistent_keyword_xyz",),
        ).fetchall()
        conn.close()
        assert len(rows) == 0
