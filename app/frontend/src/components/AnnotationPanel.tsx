import { useState, useEffect } from "react";
import type { Annotation } from "../types";
import { getAnnotations, createAnnotation, deleteAnnotation } from "../services/api";

interface Props {
  imageId: number;
}

export default function AnnotationPanel({ imageId }: Props) {
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [tag, setTag] = useState("");
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);

  const fetchAnnotations = async () => {
    try {
      const data = await getAnnotations(imageId);
      setAnnotations(data);
    } catch (err) {
      console.error("Failed to fetch annotations:", err);
    }
  };

  useEffect(() => {
    fetchAnnotations();
  }, [imageId]);

  const handleAdd = async () => {
    if (!tag.trim() && !note.trim()) return;
    setSaving(true);
    try {
      await createAnnotation(imageId, {
        tag: tag.trim() || undefined,
        note: note.trim() || undefined,
      });
      setTag("");
      setNote("");
      fetchAnnotations();
    } catch (err) {
      console.error("Failed to add annotation:", err);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteAnnotation(id);
      fetchAnnotations();
    } catch (err) {
      console.error("Failed to delete annotation:", err);
    }
  };

  return (
    <div className="mt-4">
      <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-1.5">
        <span className="w-2 h-2 bg-orange-400 rounded-full" />
        Designer Annotations
      </h4>

      {/* Existing annotations */}
      {annotations.length > 0 && (
        <div className="space-y-2 mb-3">
          {annotations.map((ann) => (
            <div
              key={ann.id}
              className="bg-orange-50 border border-orange-200 rounded-lg p-2.5 text-sm relative group"
            >
              {ann.tag && (
                <span className="inline-block bg-orange-200 text-orange-800 text-xs px-2 py-0.5 rounded mr-2">
                  {ann.tag}
                </span>
              )}
              {ann.note && <p className="text-gray-700 mt-1">{ann.note}</p>}
              <button
                onClick={() => handleDelete(ann.id)}
                className="absolute top-1 right-1 text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              {ann.created_at && (
                <p className="text-xs text-gray-400 mt-1">
                  {new Date(ann.created_at).toLocaleDateString()}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add annotation form */}
      <div className="space-y-2 bg-gray-50 rounded-lg p-3">
        <input
          type="text"
          placeholder="Tag (e.g. inspiration, reference)"
          value={tag}
          onChange={(e) => setTag(e.target.value)}
          className="w-full text-sm border border-gray-300 rounded px-3 py-1.5 focus:ring-1 focus:ring-orange-400"
        />
        <textarea
          placeholder="Add a note or observation..."
          value={note}
          onChange={(e) => setNote(e.target.value)}
          rows={2}
          className="w-full text-sm border border-gray-300 rounded px-3 py-1.5 focus:ring-1 focus:ring-orange-400 resize-none"
        />
        <button
          onClick={handleAdd}
          disabled={(!tag.trim() && !note.trim()) || saving}
          className="text-sm bg-orange-500 text-white px-3 py-1.5 rounded hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? "Saving..." : "Add Annotation"}
        </button>
      </div>
    </div>
  );
}
