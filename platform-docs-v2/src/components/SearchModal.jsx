import { useState, useRef, useEffect } from 'react';
import { search } from '../lib/search.js';

export default function SearchModal({ onClose, onNavigate }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);
  const resultsRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    const r = search(query);
    setResults(r);
    setSelectedIndex(0);
  }, [query]);

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(i => Math.min(i + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(i => Math.max(i - 1, 0));
    } else if (e.key === 'Enter' && results[selectedIndex]) {
      onNavigate(results[selectedIndex].path);
    }
  };

  // Scroll selected result into view
  useEffect(() => {
    if (resultsRef.current) {
      const el = resultsRef.current.querySelector(`[data-index="${selectedIndex}"]`);
      el?.scrollIntoView({ block: 'nearest' });
    }
  }, [selectedIndex]);

  return (
    <div
      className="fixed inset-0 bg-black/40 z-50 flex items-start justify-center pt-[15vh]"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Search documentation"
    >
      <div
        className="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] shadow-xl w-full max-w-lg mx-4 max-h-[60vh] flex flex-col"
        onClick={e => e.stopPropagation()}
      >
        {/* Search input */}
        <div className="flex items-center gap-2 px-4 py-3 border-b border-[var(--color-border)]">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" className="text-[var(--color-text-secondary)] flex-shrink-0">
            <circle cx="7" cy="7" r="5" />
            <path d="M11 11L14 14" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search documentation..."
            className="flex-1 bg-transparent border-none outline-none text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)]"
            aria-label="Search query"
            autoComplete="off"
          />
          <kbd className="text-xs text-[var(--color-text-secondary)] border border-[var(--color-border)] rounded px-1.5 flex-shrink-0">ESC</kbd>
        </div>

        {/* Results */}
        <div ref={resultsRef} className="overflow-y-auto flex-1 p-2" role="listbox" aria-label="Search results">
          {query.length < 2 ? (
            <p className="text-xs text-[var(--color-text-secondary)] px-2 py-4 text-center">
              Type at least 2 characters to search
            </p>
          ) : results.length === 0 ? (
            <p className="text-xs text-[var(--color-text-secondary)] px-2 py-4 text-center">
              No results found for "{query}"
            </p>
          ) : (
            results.map((result, idx) => (
              <button
                key={result.id}
                data-index={idx}
                role="option"
                aria-selected={idx === selectedIndex}
                className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  idx === selectedIndex
                    ? 'bg-[var(--color-brand)]/10 text-[var(--color-brand)]'
                    : 'text-[var(--color-text-primary)] hover:bg-[var(--color-bg)]'
                }`}
                onClick={() => onNavigate(result.path)}
                onMouseEnter={() => setSelectedIndex(idx)}
              >
                <div className="font-medium">{result.title}</div>
                <div className="text-xs text-[var(--color-text-secondary)] mt-0.5">
                  {result.path} · {result.headings.length} sections
                </div>
              </button>
            ))
          )}
        </div>

        {/* Footer hint */}
        <div className="border-t border-[var(--color-border)] px-4 py-2 text-xs text-[var(--color-text-secondary)] flex items-center gap-4">
          <span>↑↓ Navigate</span>
          <span>↵ Open</span>
          <span>ESC Close</span>
        </div>
      </div>
    </div>
  );
}
