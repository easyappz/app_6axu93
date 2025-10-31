import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../state/authContext';

function Header({ onLoginClick }) {
  const { user, logout } = useAuth();

  return (
    <header data-easytag="id1-react/src/components/Header.jsx" className="sticky top-0 z-30 backdrop-blur bg-white/70 border-b border-black/5">
      <div data-easytag="id2-react/src/components/Header.jsx" className="container mx-auto px-6 md:px-10 lg:px-14">
        <nav data-easytag="id3-react/src/components/Header.jsx" className="flex items-center justify-between h-16">
          <div data-easytag="id4-react/src/components/Header.jsx" className="flex items-center gap-6">
            <Link data-easytag="id5-react/src/components/Header.jsx" to="/" className="text-xl font-semibold tracking-tight hover:opacity-80 transition-opacity">Авитолог</Link>
          </div>
          <div data-easytag="id6-react/src/components/Header.jsx" className="flex items-center gap-4">
            {user ? (
              <div data-easytag="id7-react/src/components/Header.jsx" className="flex items-center gap-4">
                <span data-easytag="id8-react/src/components/Header.jsx" className="text-sm text-neutral-600">{user.email}</span>
                <button data-easytag="id9-react/src/components/Header.jsx" onClick={logout} className="px-4 py-2 rounded-full bg-black text-white text-sm hover:bg-neutral-800 transition-colors">Выйти</button>
              </div>
            ) : (
              <button data-easytag="id10-react/src/components/Header.jsx" onClick={onLoginClick} className="px-4 py-2 rounded-full bg-black text-white text-sm hover:bg-neutral-800 transition-colors">Войти</button>
            )}
          </div>
        </nav>
      </div>
    </header>
  );
}

export default Header;
