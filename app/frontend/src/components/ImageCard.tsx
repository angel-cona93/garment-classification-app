import type { GarmentImage } from "../types";
import { getImageUrl } from "../services/api";

interface Props {
  image: GarmentImage;
  onClick: (image: GarmentImage) => void;
}

export default function ImageCard({ image, onClick }: Props) {
  const isProcessing = image.status === "pending" || image.status === "processing";
  const isError = image.status === "error";

  return (
    <div
      onClick={() => onClick(image)}
      className="group cursor-pointer bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
    >
      <div className="aspect-[3/4] bg-gray-100 relative overflow-hidden">
        <img
          src={getImageUrl(image.id)}
          alt={image.original_filename || "Fashion image"}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />
        {isProcessing && (
          <div className="absolute inset-0 bg-white/70 flex items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <div className="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
              <span className="text-xs text-gray-600">Classifying...</span>
            </div>
          </div>
        )}
        {isError && (
          <div className="absolute inset-0 bg-red-50/80 flex items-center justify-center">
            <div className="flex flex-col items-center gap-1 px-3">
              <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <span className="text-xs font-medium text-red-700">Classification failed</span>
            </div>
          </div>
        )}
      </div>
      <div className="p-2.5">
        {isError && (
          <p className="text-xs text-red-600 truncate" title={image.error_message || "Classification failed"}>
            {image.error_message || "Classification failed"}
          </p>
        )}
        {image.garment_type && (
          <p className="text-sm font-medium text-gray-900 capitalize truncate">
            {image.garment_type}
          </p>
        )}
        <div className="flex flex-wrap gap-1 mt-1">
          {image.style && (
            <span className="text-xs bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded capitalize">
              {image.style}
            </span>
          )}
          {image.season && (
            <span className="text-xs bg-green-50 text-green-700 px-1.5 py-0.5 rounded">
              {image.season}
            </span>
          )}
          {image.pattern && (
            <span className="text-xs bg-amber-50 text-amber-700 px-1.5 py-0.5 rounded capitalize">
              {image.pattern}
            </span>
          )}
        </div>
        {!image.garment_type && !isProcessing && !isError && (
          <p className="text-xs text-gray-400 italic">Pending classification</p>
        )}
      </div>
    </div>
  );
}
