import { useState, useEffect } from "react";
import type { GarmentImage } from "../types";
import { getImage, getImageUrl, deleteImage } from "../services/api";
import AnnotationPanel from "./AnnotationPanel";

interface Props {
  image: GarmentImage;
  onClose: () => void;
  onDeleted: () => void;
}

const ATTR_CONFIG: { key: keyof GarmentImage; label: string; color: string }[] = [
  { key: "garment_type", label: "Type", color: "bg-indigo-50 text-indigo-700" },
  { key: "style", label: "Style", color: "bg-purple-50 text-purple-700" },
  { key: "material", label: "Material", color: "bg-blue-50 text-blue-700" },
  { key: "color_palette", label: "Colors", color: "bg-pink-50 text-pink-700" },
  { key: "pattern", label: "Pattern", color: "bg-amber-50 text-amber-700" },
  { key: "season", label: "Season", color: "bg-green-50 text-green-700" },
  { key: "occasion", label: "Occasion", color: "bg-teal-50 text-teal-700" },
  { key: "consumer_profile", label: "Consumer", color: "bg-rose-50 text-rose-700" },
  { key: "trend_notes", label: "Trends", color: "bg-cyan-50 text-cyan-700" },
];

export default function ImageDetail({ image: initialImage, onClose, onDeleted }: Props) {
  const [image, setImage] = useState(initialImage);
  const [deleting, setDeleting] = useState(false);

  // Poll if still processing
  useEffect(() => {
    if (image.status !== "pending" && image.status !== "processing") return;
    const interval = setInterval(async () => {
      try {
        const updated = await getImage(image.id);
        setImage(updated);
        if (updated.status === "classified" || updated.status === "error") {
          clearInterval(interval);
        }
      } catch {
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [image.id, image.status]);

  const handleDelete = async () => {
    if (!confirm("Delete this image?")) return;
    setDeleting(true);
    try {
      await deleteImage(image.id);
      onDeleted();
    } catch (err) {
      console.error("Delete failed:", err);
    } finally {
      setDeleting(false);
    }
  };

  const locationParts = [image.location_city, image.location_country, image.location_continent].filter(Boolean);

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-white rounded-xl shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex flex-col md:flex-row">
          {/* Image */}
          <div className="md:w-1/2 bg-gray-100">
            <img
              src={getImageUrl(image.id)}
              alt={image.original_filename || "Fashion image"}
              className="w-full h-full object-contain max-h-[70vh]"
            />
          </div>

          {/* Details */}
          <div className="md:w-1/2 p-6 overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-900 capitalize">
                  {image.garment_type || image.original_filename || "Image"}
                </h2>
                {image.uploaded_at && (
                  <p className="text-xs text-gray-400 mt-0.5">
                    Uploaded {new Date(image.uploaded_at).toLocaleDateString()}
                  </p>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleDelete}
                  disabled={deleting}
                  className="text-gray-400 hover:text-red-500 p-1"
                  title="Delete image"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
                <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-1">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Status */}
            {(image.status === "pending" || image.status === "processing") && (
              <div className="flex items-center gap-2 mb-4 bg-indigo-50 rounded-lg p-3">
                <div className="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                <span className="text-sm text-indigo-700">Classifying image...</span>
              </div>
            )}

            {image.status === "error" && (
              <div className="mb-4 bg-red-50 rounded-lg p-3">
                <p className="text-sm font-medium text-red-800">Classification failed</p>
                {image.error_message && (
                  <pre className="mt-1 text-xs text-red-600 whitespace-pre-wrap break-words font-mono bg-red-100/50 rounded p-2">
                    {image.error_message}
                  </pre>
                )}
                <p className="mt-2 text-xs text-red-500">You can still add annotations manually.</p>
              </div>
            )}

            {/* AI Description */}
            {image.description && (
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-1 flex items-center gap-1.5">
                  <span className="w-2 h-2 bg-indigo-500 rounded-full" />
                  AI Description
                </h4>
                <p className="text-sm text-gray-600 leading-relaxed">{image.description}</p>
              </div>
            )}

            {/* AI Attributes */}
            {image.status === "classified" && (
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-1.5">
                  <span className="w-2 h-2 bg-indigo-500 rounded-full" />
                  AI Attributes
                </h4>
                <div className="space-y-1.5">
                  {ATTR_CONFIG.map(({ key, label, color }) => {
                    const val = image[key];
                    if (!val) return null;
                    return (
                      <div key={key} className="flex items-start gap-2">
                        <span className="text-xs text-gray-500 w-16 shrink-0 pt-0.5">{label}</span>
                        <span className={`text-xs px-2 py-0.5 rounded capitalize ${color}`}>
                          {String(val)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Context metadata */}
            {(locationParts.length > 0 || image.designer || image.image_year) && (
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-1">Context</h4>
                <div className="text-sm text-gray-600 space-y-0.5">
                  {locationParts.length > 0 && <p>Location: {locationParts.join(", ")}</p>}
                  {image.designer && <p>Designer: {image.designer}</p>}
                  {image.image_year && (
                    <p>
                      Date: {image.image_month ? `${image.image_month}/` : ""}
                      {image.image_year}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Annotations */}
            <AnnotationPanel imageId={image.id} />
          </div>
        </div>
      </div>
    </div>
  );
}
