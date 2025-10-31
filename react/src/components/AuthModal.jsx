import React, { useState } from 'react';
import { useAuth } from '../state/authContext';

function AuthModal({ onClose }) {
  const { loginWithCredentials, registerWithCredentials } = useAuth();
  const [tab, setTab] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (tab === 'login') {
        await loginWithCredentials({ email, password });
      } else {
        await registerWithCredentials({ email, password, name });
      }
      onClose();
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Ошибка. Проверьте данные и попробуйте снова.';
      setError(typeof msg === 'string' ? msg : 'Ошибка авторизации');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-easytag="id1-react/src/components/AuthModal.jsx" className="fixed inset-0 z-50 flex items-center justify-center">
      <div data-easytag="id2-react/src/components/AuthModal.jsx" className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div data-easytag="id3-react/src/components/AuthModal.jsx" className="relative w-full max-w-md mx-auto rounded-2xl bg-white p-6 shadow-soft">
        <div data-easytag="id4-react/src/components/AuthModal.jsx" className="flex items-center justify-between mb-6">
          <h2 data-easytag="id5-react/src/components/AuthModal.jsx" className="text-lg font-semibold">{tab === 'login' ? 'Вход' : 'Регистрация'}</h2>
          <button data-easytag="id6-react/src/components/AuthModal.jsx" onClick={onClose} className="p-2 rounded-full hover:bg-neutral-100">✕</button>
        </div>
        <div data-easytag="id7-react/src/components/AuthModal.jsx" className="grid grid-cols-2 gap-2 mb-6">
          <button data-easytag="id8-react/src/components/AuthModal.jsx" onClick={() => setTab('login')} className={`px-4 py-2 rounded-xl border ${tab === 'login' ? 'bg-black text-white' : 'bg-white text-black hover:bg-neutral-50'}`}>Вход</button>
          <button data-easytag="id9-react/src/components/AuthModal.jsx" onClick={() => setTab('register')} className={`px-4 py-2 rounded-xl border ${tab === 'register' ? 'bg-black text-white' : 'bg-white text-black hover:bg-neutral-50'}`}>Регистрация</button>
        </div>
        <form data-easytag="id10-react/src/components/AuthModal.jsx" onSubmit={onSubmit} className="space-y-4">
          {tab === 'register' && (
            <div data-easytag="id11-react/src/components/AuthModal.jsx" className="space-y-2">
              <label data-easytag="id12-react/src/components/AuthModal.jsx" className="text-sm text-neutral-600">Имя (необязательно)</label>
              <input data-easytag="id13-react/src/components/AuthModal.jsx" type="text" value={name} onChange={(e) => setName(e.target.value)} className="w-full rounded-xl border px-4 py-3 focus:ring-0 focus:outline-none" placeholder="Иван" />
            </div>
          )}
          <div data-easytag="id14-react/src/components/AuthModal.jsx" className="space-y-2">
            <label data-easytag="id15-react/src/components/AuthModal.jsx" className="text-sm text-neutral-600">Email</label>
            <input data-easytag="id16-react/src/components/AuthModal.jsx" type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full rounded-xl border px-4 py-3 focus:ring-0 focus:outline-none" placeholder="you@example.com" required />
          </div>
          <div data-easytag="id17-react/src/components/AuthModal.jsx" className="space-y-2">
            <label data-easytag="id18-react/src/components/AuthModal.jsx" className="text-sm text-neutral-600">Пароль</label>
            <input data-easytag="id19-react/src/components/AuthModal.jsx" type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-xl border px-4 py-3 focus:ring-0 focus:outline-none" placeholder="••••••••" required />
          </div>
          {error && (
            <p data-easytag="id20-react/src/components/AuthModal.jsx" className="text-sm text-red-600">{error}</p>
          )}
          <button data-easytag="id21-react/src/components/AuthModal.jsx" type="submit" disabled={loading} className="w-full rounded-xl bg-black text-white py-3 hover:bg-neutral-800 transition-colors disabled:opacity-60">
            {loading ? 'Подождите…' : (tab === 'login' ? 'Войти' : 'Создать аккаунт')}
          </button>
        </form>
      </div>
    </div>
  );
}

export default AuthModal;
