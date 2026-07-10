import { Link } from 'react-router-dom';
import { flattenSidebar } from '../lib/sidebar-config.js';

const flatItems = flattenSidebar();

export default function PrevNextNav({ currentPath }) {
  const currentIndex = flatItems.findIndex(item => item.id === currentPath);

  if (currentIndex === -1) return null;

  const prev = currentIndex > 0 ? flatItems[currentIndex - 1] : null;
  const next = currentIndex < flatItems.length - 1 ? flatItems[currentIndex + 1] : null;

  return (
    <nav className="flex items-center justify-between gap-4" aria-label="Previous and next pages">
      <div>
        {prev ? (
          <Link
            to={`/docs/${prev.id}`}
            className="group flex flex-col gap-1 px-4 py-3 rounded-xl border border-[var(--color-border)] hover:border-[var(--color-brand)] transition-colors"
          >
            <span className="text-xs text-[var(--color-text-secondary)]">Previous</span>
            <span className="text-sm font-medium text-[var(--color-text-primary)] group-hover:text-[var(--color-brand)]">
              ← {prev.label}
            </span>
          </Link>
        ) : <div />}
      </div>
      <div>
        {next ? (
          <Link
            to={`/docs/${next.id}`}
            className="group flex flex-col gap-1 px-4 py-3 rounded-xl border border-[var(--color-border)] hover:border-[var(--color-brand)] transition-colors text-right"
          >
            <span className="text-xs text-[var(--color-text-secondary)]">Next</span>
            <span className="text-sm font-medium text-[var(--color-text-primary)] group-hover:text-[var(--color-brand)]">
              {next.label} →
            </span>
          </Link>
        ) : <div />}
      </div>
    </nav>
  );
}
