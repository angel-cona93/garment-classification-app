import { useState, useRef } from "react";
import { uploadImage } from "../services/api";

interface Props {
  onUploadComplete: () => void;
  onClose: () => void;
}

export default function UploadPanel({ onUploadComplete, onClose }: Props) {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [context, setContext] = useState({
    location_continent: "",
    location_country: "",
    location_city: "",
    designer: "",
    image_year: "",
    image_month: "",
  });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files).filter((f) =>
      f.type.startsWith("image/")
    );
    setFiles((prev) => [...prev, ...dropped]);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles((prev) => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setUploading(true);
    try {
      const ctx: Record<string, string | number | undefined> = {};
      if (context.location_continent) ctx.location_continent = context.location_continent;
      if (context.location_country) ctx.location_country = context.location_country;
      if (context.location_city) ctx.location_city = context.location_city;
      if (context.designer) ctx.designer = context.designer;
      if (context.image_year) ctx.image_year = parseInt(context.image_year);
      if (context.image_month) ctx.image_month = parseInt(context.image_month);

      for (const file of files) {
        await uploadImage(file, ctx);
      }
      setFiles([]);
      onUploadComplete();
      onClose();
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Upload Images</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Drop zone */}
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-indigo-400 transition-colors"
          >
            <svg className="mx-auto h-10 w-10 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 16v-8m0 0l-3 3m3-3l3 3M3 16.5V18a2.25 2.25 0 002.25 2.25h13.5A2.25 2.25 0 0021 18v-1.5m-18 0V7.875c0-.621.504-1.125 1.125-1.125H6.75l1.5-2.25h7.5l1.5 2.25h2.625c.621 0 1.125.504 1.125 1.125V16.5" />
            </svg>
            <p className="text-sm text-gray-600">
              Drag & drop images or <span className="text-indigo-600 font-medium">browse</span>
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* File list */}
          {files.length > 0 && (
            <div className="mt-3 space-y-1">
              {files.map((f, i) => (
                <div key={i} className="flex items-center justify-between text-sm text-gray-600 bg-gray-50 rounded px-3 py-1.5">
                  <span className="truncate">{f.name}</span>
                  <button
                    onClick={() => setFiles((prev) => prev.filter((_, j) => j !== i))}
                    className="text-gray-400 hover:text-red-500 ml-2"
                  >
                    &times;
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Context fields */}
          <div className="mt-4 space-y-3">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Optional Context</p>
            <div className="grid grid-cols-2 gap-2">
              <input placeholder="Continent" value={context.location_continent} onChange={(e) => setContext((p) => ({ ...p, location_continent: e.target.value }))} className="text-sm border border-gray-300 rounded px-3 py-1.5 focus:ring-1 focus:ring-indigo-500" />
              <input placeholder="Country" value={context.location_country} onChange={(e) => setContext((p) => ({ ...p, location_country: e.target.value }))} className="text-sm border border-gray-300 rounded px-3 py-1.5 focus:ring-1 focus:ring-indigo-500" />
              <input placeholder="City" value={context.location_city} onChange={(e) => setContext((p) => ({ ...p, location_city: e.target.value }))} className="text-sm border border-gray-300 rounded px-3 py-1.5 focus:ring-1 focus:ring-indigo-500" />
              <input placeholder="Designer" value={context.designer} onChange={(e) => setContext((p) => ({ ...p, designer: e.target.value }))} className="text-sm border border-gray-300 rounded px-3 py-1.5 focus:ring-1 focus:ring-indigo-500" />
              <input placeholder="Year (e.g. 2025)" type="number" value={context.image_year} onChange={(e) => setContext((p) => ({ ...p, image_year: e.target.value }))} className="text-sm border border-gray-300 rounded px-3 py-1.5 focus:ring-1 focus:ring-indigo-500" />
              <input placeholder="Month (1-12)" type="number" min="1" max="12" value={context.image_month} onChange={(e) => setContext((p) => ({ ...p, image_month: e.target.value }))} className="text-sm border border-gray-300 rounded px-3 py-1.5 focus:ring-1 focus:ring-indigo-500" />
            </div>
          </div>

          {/* Upload button */}
          <button
            onClick={handleUpload}
            disabled={files.length === 0 || uploading}
            className="mt-4 w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          >
            {uploading ? "Uploading..." : `Upload ${files.length} image${files.length !== 1 ? "s" : ""}`}
          </button>
        </div>
      </div>
    </div>
  );
}
