import React, { useEffect, useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header.jsx';
import Home from './pages/Home.jsx';
import Listing from './pages/Listing.jsx';
import NotFound from './pages/NotFound.jsx';
import AuthModal from './components/AuthModal.jsx';

function App() {
  const [authOpen, setAuthOpen] = useState(false);

  useEffect(() => {
    const routes = ['/', '/ad/:id', '*'];
    if (typeof window.handleRoutes === 'function') {
      window.handleRoutes(routes);
    }
  }, []);

  return (
    <div data-easytag="id1-react/src/App.jsx" className="min-h-screen bg-neutralBg">
      <Header data-easytag="id2-react/src/App.jsx" onLoginClick={() => setAuthOpen(true)} />
      <main data-easytag="id3-react/src/App.jsx" className="container mx-auto px-6 md:px-10 lg:px-14 py-10">
        <Routes>
          <Route path="/" element={<Home data-easytag="id4-react/src/App.jsx" onRequireAuth={() => setAuthOpen(true)} />} />
          <Route path="/ad/:id" element={<Listing data-easytag="id5-react/src/App.jsx" onRequireAuth={() => setAuthOpen(true)} />} />
          <Route path="*" element={<NotFound data-easytag="id6-react/src/App.jsx" />} />
        </Routes>
      </main>
      {authOpen && (
        <AuthModal data-easytag="id7-react/src/App.jsx" onClose={() => setAuthOpen(false)} />)
      }
      <footer data-easytag="id8-react/src/App.jsx" className="py-10 text-center text-sm text-neutral-500">
        <p data-easytag="id9-react/src/App.jsx">© {new Date().getFullYear()} Авитолог</p>
      </footer>
    </div>
  );
}

export default App;
