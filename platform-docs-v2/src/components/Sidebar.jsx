import { NavLink, useLocation } from 'react-router-dom';
import sidebarConfig from '../lib/sidebar-config.js';

export default function Sidebar({ open, onClose }) {
  const location = useLocation();

  const isActive = (id) => {
    const docPath = `/docs/${id}`;
    return location.pathname === docPath || location.pathname.startsWith(docPath + '/');
  };

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/30 z-40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed lg:sticky top-14 left-0 z-40
          w-72 h-[calc(100vh-3.5rem)]
          bg-[var(--color-surface)] border-r border-[var(--color-border)]
          overflow-y-auto
          transition-transform duration-200 ease-in-out
          ${open ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0
        `}
        aria-label="Documentation navigation"
      >
        <nav className="py-4 px-3">
          <ul className="space-y-1">
            {sidebarConfig.map((item, idx) => (
              <li key={idx}>
                {item.type === 'doc' ? (
                  <NavLink
                    to={`/docs/${item.id}`}
                    onClick={onClose}
                    className={({ isActive: active }) =>
                      `block px-3 py-2 rounded-xl text-sm font-medium transition-colors ${
                        active
                          ? 'bg-[var(--color-brand)]/10 text-[var(--color-brand)]'
                          : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg)]'
                      }`
                    }
                  >
                    {item.label}
                  </NavLink>
                ) : (
                  <div className="mt-4 mb-1">
                    <div className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-[var(--color-text-secondary)]">
                      {item.label}
                    </div>
                    <ul className="space-y-0.5 ml-0">
                      {item.items.map((childId) => {
                        const label = childId.split('/').pop()
                          .replace(/-/g, ' ')
                          .replace(/\b\w/g, l => l.toUpperCase());
                        return (
                          <li key={childId}>
                            <NavLink
                              to={`/docs/${childId}`}
                              onClick={onClose}
                              className={({ isActive: active }) =>
                                `block px-3 py-1.5 rounded-xl text-sm transition-colors ${
                                  active
                                    ? 'bg-[var(--color-brand)]/10 text-[var(--color-brand)] font-medium'
                                    : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg)]'
                                }`
                              }
                            >
                              {label}
                            </NavLink>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </nav>

        <div className="border-t border-[var(--color-border)] px-3 py-3 text-xs text-[var(--color-text-secondary)]">
          <p>ZoTok Platform Manual v1.0</p>
          <p className="mt-1">
            <a href="https://github.com/rrake5212/zotok-platform-docs" className="hover:text-[var(--color-brand)]">GitHub</a>
          </p>
        </div>
      </aside>
    </>
  );
}
