import { useState, useEffect } from "react";
import type { FilterOptions } from "../types";
import { getFilters } from "../services/api";

export function useFilterOptions() {
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({});
  const [loading, setLoading] = useState(false);

  const fetchFilters = async () => {
    setLoading(true);
    try {
      const data = await getFilters();
      setFilterOptions(data);
    } catch (err) {
      console.error("Failed to fetch filters:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFilters();
  }, []);

  return { filterOptions, loading, refresh: fetchFilters };
}
