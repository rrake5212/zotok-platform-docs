import { Link } from 'react-router-dom';
import sidebarConfig from '../lib/sidebar-config.js';

export default function HomePage() {
  // Get the first few categories for quick links
  const quickCategories = sidebarConfig.filter(item => item.type === 'category').slice(0, 4);

  return (
    <div className="max-w-screen-xl mx-auto px-4 lg:px-8 py-12">
      {/* Hero */}
      <div className="mb-16">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-2xl bg-[var(--color-brand)] flex items-center justify-center text-white font-bold text-xl">
            Z
          </div>
          <div>
            <h1 className="text-3xl font-bold text-[var(--color-text-primary)]">ZoTok Platform Manual</h1>
            <p className="text-[var(--color-text-secondary)] mt-1">
              Field Operations &amp; Distributor Management Platform
            </p>
          </div>
        </div>
        <p className="text-lg text-[var(--color-text-secondary)] max-w-2xl">
          Complete documentation for the ZoTok platform — covering everything from getting started
          to advanced configuration. Each page focuses on one task with clear, sequential instructions.
        </p>
      </div>

      {/* Quick start */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">Getting Started</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Link
            to="/docs/getting-started/login"
            className="p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-brand)] transition-colors group"
          >
            <div className="text-2xl mb-2">🔐</div>
            <h3 className="font-medium text-[var(--color-text-primary)] group-hover:text-[var(--color-brand)]">Login to ZoTok</h3>
            <p className="text-sm text-[var(--color-text-secondary)] mt-1">Access the platform with your credentials</p>
          </Link>
          <Link
            to="/docs/dashboard/overview"
            className="p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-brand)] transition-colors group"
          >
            <div className="text-2xl mb-2">📊</div>
            <h3 className="font-medium text-[var(--color-text-primary)] group-hover:text-[var(--color-brand)]">Dashboard Overview</h3>
            <p className="text-sm text-[var(--color-text-secondary)] mt-1">Understand your KPIs at a glance</p>
          </Link>
          <Link
            to="/docs/threads/overview"
            className="p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-brand)] transition-colors group"
          >
            <div className="text-2xl mb-2">🧵</div>
            <h3 className="font-medium text-[var(--color-text-primary)] group-hover:text-[var(--color-brand)]">Using Threads</h3>
            <p className="text-sm text-[var(--color-text-secondary)] mt-1">AI-powered queries and data analysis</p>
          </Link>
        </div>
      </div>

      {/* Module categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {quickCategories.map((cat, idx) => (
          <div key={idx}>
            <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-3">{cat.label}</h2>
            <ul className="space-y-1">
              {cat.items.map((itemId) => {
                const label = itemId.split('/').pop()
                  .replace(/-/g, ' ')
                  .replace(/\b\w/g, l => l.toUpperCase());
                return (
                  <li key={itemId}>
                    <Link
                      to={`/docs/${itemId}`}
                      className="block px-3 py-2 rounded-lg text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-brand)] hover:bg-[var(--color-surface)] transition-colors"
                    >
                      {label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>

      {/* Full doc link */}
      <div className="mt-12 p-6 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-2">Browse All Documentation</h2>
        <p className="text-sm text-[var(--color-text-secondary)] mb-4">
          Use the sidebar navigation to explore all modules, reports, and configuration guides.
        </p>
        <Link
          to="/docs/intro"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[var(--color-brand)] text-white text-sm font-medium hover:opacity-90 transition-opacity"
        >
          View Full Manual
          <svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M7 4l6 6-6 6" />
          </svg>
        </Link>
      </div>
    </div>
  );
}
