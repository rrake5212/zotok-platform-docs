import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { getDocHeadings } from '../lib/content-loader.js';

export default function TableOfContents({ docPath }) {
  const [activeId, setActiveId] = useState('');
  const location = useLocation();
  const headings = getDocHeadings(docPath);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        }
      },
      { rootMargin: '-80px 0px -80% 0px' }
    );

    const elements = document.querySelectorAll('h2[id], h3[id], h4[id]');
    elements.forEach(el => observer.observe(el));

    return () => observer.disconnect();
  }, [docPath, location.pathname]);

  if (!headings || headings.length === 0) {
    return null;
  }

  return (
    <nav className="w-56 flex-shrink-0 hidden xl:block" aria-label="Table of contents">
      <div className="sticky top-20 overflow-y-auto max-h-[calc(100vh-6rem)]">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--color-text-secondary)] mb-3 px-1">
          On this page
        </h3>
        <ul className="space-y-1">
          {headings.map((h, i) => (
            <li key={i} style={{ paddingLeft: `${(h.level - 2) * 12}px` }}>
              <a
                href={`#${h.id}`}
                className={`block text-sm py-1 px-2 rounded-lg transition-colors ${
                  activeId === h.id
                    ? 'text-[var(--color-brand)] font-medium'
                    : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
                }`}
                onClick={(e) => {
                  e.preventDefault();
                  const el = document.getElementById(h.id);
                  if (el) {
                    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    el.classList.add('heading-highlight');
                    setTimeout(() => el.classList.remove('heading-highlight'), 2000);
                    window.history.replaceState(null, '', `#${h.id}`);
                  }
                }}
              >
                {h.text}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
