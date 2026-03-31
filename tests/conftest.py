import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app", "backend"))

from database import init_db, get_connection


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


@pytest.fixture
def db(db_path):
    conn = get_connection(db_path)
    yield conn
    conn.close()


@pytest.fixture
def seeded_db(db_path):
    """Pre-populated DB with 10 sample images for filter/search tests."""
    conn = get_connection(db_path)

    images = [
        ("img1.jpg", "/uploads/img1.jpg", "photo1.jpg", "A red silk dress",
         "dress", "formal", "silk", "red, gold", "solid", "fall/winter",
         "evening", "luxury", "quiet luxury", "Asia", "Japan", "Tokyo",
         "Designer A", 2025, 3, "classified"),
        ("img2.jpg", "/uploads/img2.jpg", "photo2.jpg", "Blue denim jacket",
         "jacket", "streetwear", "denim", "blue, white", "solid", "transitional",
         "casual", "young professional", "oversized silhouettes", "Europe", "France", "Paris",
         "Designer B", 2025, 6, "classified"),
        ("img3.jpg", "/uploads/img3.jpg", "photo3.jpg", "Floral cotton skirt",
         "skirt", "bohemian", "cotton", "green, pink, white", "floral", "spring/summer",
         "casual", "teen", "cottagecore", "Asia", "Japan", "Kyoto",
         "Designer A", 2024, 9, "classified"),
        ("img4.jpg", "/uploads/img4.jpg", "photo4.jpg", "Black leather coat",
         "coat", "minimalist", "leather", "black", "solid", "fall/winter",
         "office", "mature", "quiet luxury", "Europe", "Italy", "Milan",
         "Designer C", 2025, 1, "classified"),
        ("img5.jpg", "/uploads/img5.jpg", "photo5.jpg", "Striped linen shirt",
         "shirt", "casual", "linen", "white, blue", "striped", "spring/summer",
         "casual", "young professional", "coastal grandmother", "North America", "USA", "New York",
         "Designer B", 2025, 7, "classified"),
        ("img6.jpg", "/uploads/img6.jpg", "photo6.jpg", "Embroidered wool sweater",
         "knitwear", "vintage", "wool", "cream, burgundy", "geometric", "fall/winter",
         "casual", "mature", "folk revival", "Europe", "UK", "London",
         None, 2024, 11, "classified"),
        ("img7.jpg", "/uploads/img7.jpg", "photo7.jpg", "Velvet evening gown",
         "dress", "romantic", "velvet", "deep purple, silver", "solid", "fall/winter",
         "evening", "luxury", "maximalism", "Europe", "France", "Paris",
         "Designer A", 2025, 2, "classified"),
        ("img8.jpg", "/uploads/img8.jpg", "photo8.jpg", "Athletic crop top",
         "activewear", "sporty", "polyester", "neon green, black", "solid", "transitional",
         "athletic", "teen", "athleisure", "North America", "USA", "Los Angeles",
         None, 2025, 4, "classified"),
        ("img9.jpg", "/uploads/img9.jpg", "photo9.jpg", "Printed chiffon blouse",
         "blouse", "romantic", "chiffon", "pastel pink, lavender", "floral", "spring/summer",
         "office", "young professional", "soft girl aesthetic", "Asia", "South Korea", "Seoul",
         "Designer D", 2025, 5, "classified"),
        ("img10.jpg", "/uploads/img10.jpg", "photo10.jpg", "Plaid wool trousers",
         "trousers", "preppy", "wool", "gray, navy, red", "plaid", "fall/winter",
         "office", "young professional", "quiet luxury", "Europe", "UK", "London",
         "Designer C", 2024, 10, "classified"),
    ]

    for img in images:
        conn.execute(
            """INSERT INTO images (filename, filepath, original_filename, description,
                garment_type, style, material, color_palette, pattern, season,
                occasion, consumer_profile, trend_notes,
                location_continent, location_country, location_city,
                designer, image_year, image_month, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            img,
        )

    rows = conn.execute("SELECT id, description, garment_type, style, material, trend_notes FROM images").fetchall()
    for row in rows:
        conn.execute(
            "INSERT INTO images_fts (image_id, description, garment_type, style, material, trend_notes, annotation_text) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(row["id"]), row["description"] or "", row["garment_type"] or "", row["style"] or "", row["material"] or "", row["trend_notes"] or "", ""),
        )

    conn.commit()
    yield db_path
    conn.close()
