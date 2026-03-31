import { useState } from "react";
import type { FilterOptions, ActiveFilters } from "../types";

interface Props {
  filterOptions: FilterOptions;
  activeFilters: ActiveFilters;
  onFilterChange: (key: string, value: string) => void;
  onClear: () => void;
}

const FILTER_LABELS: Record<string, string> = {
  garment_type: "Garment Type",
  style: "Style",
  material: "Material",
  color_palette: "Color",
  pattern: "Pattern",
  season: "Season",
  occasion: "Occasion",
  consumer_profile: "Consumer Profile",
  trend_notes: "Trend Notes",
  location_continent: "Continent",
  location_country: "Country",
  location_city: "City",
  designer: "Designer",
  image_year: "Year",
  image_month: "Month",
};

function FilterSection({
  label,
  filterKey,
  values,
  activeValue,
  onChange,
}: {
  label: string;
  filterKey: string;
  values: (string | number)[];
  activeValue: string;
  onChange: (key: string, value: string) => void;
}) {
  const [expanded, setExpanded] = useState(!!activeValue);

  if (values.length === 0) return null;

  return (
    <div className="border-b border-gray-100 last:border-b-0">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full py-2 text-left"
      >
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <div className="flex items-center gap-1">
          {activeValue && (
            <span className="text-xs bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded">
              {activeValue.split(",").length}
            </span>
          )}
          <svg
            className={`w-4 h-4 text-gray-400 transition-transform ${expanded ? "rotate-180" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>
      {expanded && (
        <div className="pb-2 space-y-1 max-h-40 overflow-y-auto">
          {values.map((v) => {
            const strVal = String(v);
            const activeValues = activeValue ? activeValue.split(",") : [];
            const isActive = activeValues.includes(strVal);
            return (
              <label key={strVal} className="flex items-center gap-2 text-sm cursor-pointer hover:bg-gray-50 px-1 rounded">
                <input
                  type="checkbox"
                  checked={isActive}
                  onChange={() => {
                    let next: string[];
                    if (isActive) {
                      next = activeValues.filter((x) => x !== strVal);
                    } else {
                      next = [...activeValues, strVal];
                    }
                    onChange(filterKey, next.join(","));
                  }}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 h-3.5 w-3.5"
                />
                <span className="text-gray-600 truncate">{strVal}</span>
              </label>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function FilterSidebar({
  filterOptions,
  activeFilters,
  onFilterChange,
  onClear,
}: Props) {
  const hasActive = Object.values(activeFilters).some((v) => v);

  return (
    <div className="w-56 shrink-0 bg-white border-r border-gray-200 overflow-y-auto p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">Filters</h3>
        {hasActive && (
          <button onClick={onClear} className="text-xs text-indigo-600 hover:text-indigo-800">
            Clear all
          </button>
        )}
      </div>
      {Object.entries(FILTER_LABELS).map(([key, label]) => {
        const values = filterOptions[key] || [];
        if (values.length === 0) return null;
        return (
          <FilterSection
            key={key}
            label={label}
            filterKey={key}
            values={values}
            activeValue={activeFilters[key] || ""}
            onChange={onFilterChange}
          />
        );
      })}
    </div>
  );
}
