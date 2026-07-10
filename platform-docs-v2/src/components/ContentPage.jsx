import { useState, useEffect } from 'react';
import { useParams, useLocation, Navigate } from 'react-router-dom';
import { getDocContent } from '../lib/content-loader.js';
import TableOfContents from './TableOfContents.jsx';
import PrevNextNav from './PrevNextNav.jsx';

export default function ContentPage() {
  const { '*': splat } = useParams();
  const location = useLocation();
  const [mobileTocOpen, setMobileTocOpen] = useState(false);

  // The path is everything after /docs/
  // e.g., /docs/dashboard/overview -> dashboard/overview
  let docPath = splat || 'intro';
  // Remove trailing slash if present
  docPath = docPath.replace(/\/$/, '');
  // If path ends with a folder name (no file), try appending /overview
  if (docPath.split('/').length >= 2 && !docPath.endsWith('.md')) {
    // check if it resolves, if not try overview.md
  }

  const doc = getDocContent(docPath);

  // Handle scroll to hash on load
  useEffect(() => {
    if (location.hash) {
      const id = location.hash.slice(1);
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'start' });
          el.classList.add('heading-highlight');
          setTimeout(() => el.classList.remove('heading-highlight'), 2000);
        }
      }, 100);
    }
    window.scrollTo(0, 0);
  }, [docPath, location.hash]);

  // Auto-closing mobile TOC when clicking a link
  useEffect(() => {
    setMobileTocOpen(false);
  }, [docPath]);

  if (!doc) {
    return (
      <div className="flex-1 flex items-center justify-center py-20">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)] mb-2">Page Not Found</h1>
          <p className="text-[var(--color-text-secondary)]">
            The document <code>{docPath}</code> could not be found.
          </p>
          <a
            href="/zotok-platform-docs/"
            className="inline-block mt-4 px-4 py-2 rounded-xl bg-[var(--color-brand)] text-white text-sm font-medium"
          >
            Go to Home
          </a>
        </div>
      </div>
    );
  }

  const headings = doc.headings || [];

  return (
    <div className="flex-1 flex flex-col xl:flex-row max-w-screen-2xl mx-auto w-full px-4 lg:px-8">
      {/* Mobile TOC toggle */}
      {headings.length > 0 && (
        <div className="xl:hidden w-full mt-4 mb-2">
          <button
            onClick={() => setMobileTocOpen(!mobileTocOpen)}
            className="flex items-center gap-2 w-full px-3 py-2 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] text-sm text-[var(--color-text-secondary)]"
            aria-label="Toggle table of contents"
          >
            <span>On this page</span>
            <svg
              className={`transition-transform ${mobileTocOpen ? 'rotate-180' : ''}`}
              width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2"
            >
              <path d="M6 8l4 4 4-4" />
            </svg>
          </button>
          {mobileTocOpen && (
            <ul className="mt-2 space-y-1 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-2">
              {headings.map((h, i) => (
                <li key={i} style={{ paddingLeft: `${(h.level - 2) * 12}px` }}>
                  <a
                    href={`#${h.id}`}
                    className="block text-sm py-1 px-2 rounded-lg text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
                    onClick={(e) => {
                      e.preventDefault();
                      const el = document.getElementById(h.id);
                      if (el) el.scrollIntoView({ behavior: 'smooth' });
                      setMobileTocOpen(false);
                    }}
                  >
                    {h.text}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Main content */}
      <article className="flex-1 py-8 min-w-0">
        <div className="prose-custom mx-auto">
          {doc.rendered}
        </div>
        <div className="mt-12 pt-8 border-t border-[var(--color-border)]">
          <PrevNextNav currentPath={docPath} />
        </div>
      </article>

      {/* Desktop TOC sidebar */}
      <aside className="hidden xl:block w-56 flex-shrink-0 py-8">
        <TableOfContents docPath={docPath} />
      </aside>
    </div>
  );
}
