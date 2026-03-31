import axios from "axios";
import type {
  GarmentImage,
  Annotation,
  FilterOptions,
  ImageListResponse,
  SearchResponse,
  ActiveFilters,
} from "../types";

const api = axios.create({ baseURL: "/api" });

export async function uploadImage(
  file: File,
  context?: {
    location_continent?: string;
    location_country?: string;
    location_city?: string;
    designer?: string;
    image_year?: number;
    image_month?: number;
  }
): Promise<GarmentImage> {
  const form = new FormData();
  form.append("file", file);
  if (context) {
    for (const [key, val] of Object.entries(context)) {
      if (val !== undefined && val !== null && val !== "") {
        form.append(key, String(val));
      }
    }
  }
  const { data } = await api.post("/images/upload", form);
  return data;
}

export async function listImages(
  filters: ActiveFilters = {},
  page = 1,
  pageSize = 50
): Promise<ImageListResponse> {
  const params = new URLSearchParams();
  for (const [key, val] of Object.entries(filters)) {
    if (val) params.set(key, val);
  }
  params.set("page", String(page));
  params.set("page_size", String(pageSize));
  const { data } = await api.get(`/images?${params}`);
  return data;
}

export async function getImage(id: number): Promise<GarmentImage> {
  const { data } = await api.get(`/images/${id}`);
  return data;
}

export async function deleteImage(id: number): Promise<void> {
  await api.delete(`/images/${id}`);
}

export function getImageUrl(id: number): string {
  return `/api/images/${id}/file`;
}

export async function getFilters(): Promise<FilterOptions> {
  const { data } = await api.get("/filters");
  return data;
}

export async function searchImages(query: string): Promise<SearchResponse> {
  const { data } = await api.get("/search", { params: { q: query } });
  return data;
}

export async function getAnnotations(imageId: number): Promise<Annotation[]> {
  const { data } = await api.get(`/images/${imageId}/annotations`);
  return data;
}

export async function createAnnotation(
  imageId: number,
  body: { tag?: string; note?: string }
): Promise<Annotation> {
  const { data } = await api.post(`/images/${imageId}/annotations`, body);
  return data;
}

export async function deleteAnnotation(id: number): Promise<void> {
  await api.delete(`/annotations/${id}`);
}
