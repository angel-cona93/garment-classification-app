import { useState, useEffect, useCallback } from "react";
import { useImages } from "./hooks/useImages";
import { useFilterOptions } from "./hooks/useFilters";
import SearchBar from "./components/SearchBar";
import FilterSidebar from "./components/FilterSidebar";
import ImageGrid from "./components/ImageGrid";
import ImageDetail from "./components/ImageDetail";
import UploadPanel from "./components/UploadPanel";
import type { GarmentImage } from "./types";

export default function App() {
  const {
    images,
    total,
    loading,
    filters,
    searchQuery,
    updateFilter,
    clearFilters,
    search,
    refresh,
  } = useImages();
  const { filterOptions, refresh: refreshFilters } = useFilterOptions();

  const [showUpload, setShowUpload] = useState(false);
  const [selectedImage, setSelectedImage] = useState<GarmentImage | null>(null);

  // Auto-refresh to pick up classification results
  useEffect(() => {
    const hasProcessing = images.some(
      (img) => img.status === "pending" || img.status === "processing"
    );
    if (!hasProcessing) return;
    const interval = setInterval(() => {
      refresh();
      refreshFilters();
    }, 3000);
    return () => clearInterval(interval);
  }, [images, refresh, refreshFilters]);

  const handleUploadComplete = useCallback(() => {
    refresh();
    refreshFilters();
  }, [refresh, refreshFilters]);

  const handleImageDeleted = useCallback(() => {
    setSelectedImage(null);
    refresh();
    refreshFilters();
  }, [refresh, refreshFilters]);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4 shrink-0">
        <h1 className="text-lg font-bold text-gray-900 whitespace-nowrap">Fashion AI</h1>
        <div className="flex-1 max-w-xl">
          <SearchBar value={searchQuery} onSearch={search} />
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">
            {total} image{total !== 1 ? "s" : ""}
          </span>
          <button
            onClick={() => setShowUpload(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 text-sm font-medium flex items-center gap-1.5"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Upload
          </button>
        </div>
      </header>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        <FilterSidebar
          filterOptions={filterOptions}
          activeFilters={filters}
          onFilterChange={updateFilter}
          onClear={clearFilters}
        />
        <main className="flex-1 overflow-y-auto">
          {searchQuery && (
            <div className="px-4 pt-3 flex items-center gap-2">
              <span className="text-sm text-gray-500">
                Results for "<span className="font-medium text-gray-700">{searchQuery}</span>"
              </span>
              <button
                onClick={() => search("")}
                className="text-xs text-indigo-600 hover:text-indigo-800"
              >
                Clear
              </button>
            </div>
          )}
          <ImageGrid images={images} loading={loading} onImageClick={setSelectedImage} />
        </main>
      </div>

      {/* Modals */}
      {showUpload && (
        <UploadPanel
          onUploadComplete={handleUploadComplete}
          onClose={() => setShowUpload(false)}
        />
      )}
      {selectedImage && (
        <ImageDetail
          image={selectedImage}
          onClose={() => setSelectedImage(null)}
          onDeleted={handleImageDeleted}
        />
      )}
    </div>
  );
}
