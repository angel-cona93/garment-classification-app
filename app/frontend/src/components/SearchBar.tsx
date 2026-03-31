import { useState, useEffect } from "react";

interface Props {
  value: string;
  onSearch: (query: string) => void;
}

export default function SearchBar({ value, onSearch }: Props) {
  const [input, setInput] = useState(value);

  useEffect(() => {
    setInput(value);
  }, [value]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (input !== value) {
        onSearch(input);
      }
    }, 400);
    return () => clearTimeout(timer);
  }, [input, value, onSearch]);

  return (
    <div className="relative">
      <input
        type="text"
        placeholder='Search descriptions... e.g. "embroidered neckline"'
        value={input}
        onChange={(e) => setInput(e.target.value)}
        className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
      />
      <svg
        className="absolute left-3 top-2.5 h-4 w-4 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    </div>
  );
}
