import { useState, useCallback, useRef, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { ThemeProvider } from './lib/theme-context.jsx';
import Header from './components/Header.jsx';
import Sidebar from './components/Sidebar.jsx';
import ContentPage from './components/ContentPage.jsx';
import HomePage from './components/HomePage.jsx';
import SearchModal from './components/SearchModal.jsx';

function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const navigate = useNavigate();

  const toggleSidebar = useCallback(() => setSidebarOpen(v => !v), []);
  const closeSidebar = useCallback(() => setSidebarOpen(false), []);
  const openSearch = useCallback(() => setSearchOpen(true), []);
  const closeSearch = useCallback(() => setSearchOpen(false), []);

  const handleSearchNavigate = useCallback((path) => {
    navigate(path);
    closeSearch();
  }, [navigate, closeSearch]);

  // Keyboard shortcut for search
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(v => !v);
      }
      if (e.key === 'Escape' && searchOpen) {
        setSearchOpen(false);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [searchOpen]);

  return (
    <div className="min-h-screen flex flex-col">
      <Header
        onMenuToggle={toggleSidebar}
        onSearchToggle={openSearch}
      />

      <div className="flex flex-1 relative">
        <Sidebar open={sidebarOpen} onClose={closeSidebar} />

        <main className="flex-1 min-w-0 lg:ml-72" id="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/docs/*" element={<ContentPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>

      {searchOpen && (
        <SearchModal
          onClose={closeSearch}
          onNavigate={handleSearchNavigate}
        />
      )}
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppLayout />
    </ThemeProvider>
  );
}
