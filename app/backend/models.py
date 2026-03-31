import sqlite3
from enum import StrEnum
from pydantic import BaseModel
from typing import Optional


class ImageStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    CLASSIFIED = "classified"
    ERROR = "error"


class ImageUploadContext(BaseModel):
    location_continent: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    designer: Optional[str] = None
    image_year: Optional[int] = None
    image_month: Optional[int] = None


class ImageResponse(BaseModel):
    id: int
    filename: str
    original_filename: Optional[str] = None
    uploaded_at: Optional[str] = None
    description: Optional[str] = None
    garment_type: Optional[str] = None
    style: Optional[str] = None
    material: Optional[str] = None
    color_palette: Optional[str] = None
    pattern: Optional[str] = None
    season: Optional[str] = None
    occasion: Optional[str] = None
    consumer_profile: Optional[str] = None
    trend_notes: Optional[str] = None
    location_continent: Optional[str] = None
    location_country: Optional[str] = None
    location_city: Optional[str] = None
    designer: Optional[str] = None
    image_year: Optional[int] = None
    image_month: Optional[int] = None
    status: str = ImageStatus.PENDING
    error_message: Optional[str] = None


class AnnotationCreate(BaseModel):
    tag: Optional[str] = None
    note: Optional[str] = None


class AnnotationResponse(BaseModel):
    id: int
    image_id: int
    tag: Optional[str] = None
    note: Optional[str] = None
    created_at: Optional[str] = None


def row_to_image(row: sqlite3.Row) -> dict:
    return dict(row)


def row_to_annotation(row: sqlite3.Row) -> dict:
    return dict(row)
