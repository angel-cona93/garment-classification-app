export interface GarmentImage {
  id: number;
  filename: string;
  original_filename: string | null;
  uploaded_at: string | null;
  description: string | null;
  garment_type: string | null;
  style: string | null;
  material: string | null;
  color_palette: string | null;
  pattern: string | null;
  season: string | null;
  occasion: string | null;
  consumer_profile: string | null;
  trend_notes: string | null;
  location_continent: string | null;
  location_country: string | null;
  location_city: string | null;
  designer: string | null;
  image_year: number | null;
  image_month: number | null;
  status: string;
  error_message: string | null;
}

export interface Annotation {
  id: number;
  image_id: number;
  tag: string | null;
  note: string | null;
  created_at: string | null;
}

export interface FilterOptions {
  [key: string]: string[] | number[];
}

export interface ImageListResponse {
  images: GarmentImage[];
  total: number;
  page: number;
  page_size: number;
}

export interface SearchResponse {
  images: GarmentImage[];
  total: number;
  query: string;
}

export type ActiveFilters = Record<string, string>;
