import { useState, useEffect, useCallback } from "react";
import type { GarmentImage, ActiveFilters } from "../types";
import { listImages, searchImages } from "../services/api";

export function useImages() {
  const [images, setImages] = useState<GarmentImage[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<ActiveFilters>({});
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);

  const fetchImages = useCallback(async () => {
    setLoading(true);
    try {
      if (searchQuery.trim()) {
        const res = await searchImages(searchQuery);
        setImages(res.images);
        setTotal(res.total);
      } else {
        const res = await listImages(filters, page);
        setImages(res.images);
        setTotal(res.total);
      }
    } catch (err) {
      console.error("Failed to fetch images:", err);
    } finally {
      setLoading(false);
    }
  }, [filters, searchQuery, page]);

  useEffect(() => {
    fetchImages();
  }, [fetchImages]);

  const updateFilter = useCallback((key: string, value: string) => {
    setPage(1);
    setSearchQuery("");
    setFilters((prev) => {
      if (!value) {
        const next = { ...prev };
        delete next[key];
        return next;
      }
      return { ...prev, [key]: value };
    });
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
    setSearchQuery("");
    setPage(1);
  }, []);

  const search = useCallback((q: string) => {
    setSearchQuery(q);
    setPage(1);
  }, []);

  return {
    images,
    total,
    loading,
    filters,
    searchQuery,
    page,
    setPage,
    updateFilter,
    clearFilters,
    search,
    refresh: fetchImages,
  };
}
