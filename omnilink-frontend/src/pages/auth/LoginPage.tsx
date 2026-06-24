import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { ROLES_LIST } from '../../utils/constants';
import type { UserRole } from '../../types/crm';

export const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState<UserRole>('Admin');
  const { login } = useAuth();
  const { showToast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(username, selectedRole);
    showToast(`Access Authorized. Core session set to [${selectedRole}].`);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F3F3F3] font-sans">
      <div className="max-w-md w-full bg-white p-8 border border-gray-200 rounded-md shadow-sm">
        
        <div className="flex flex-col items-center mb-6">
          <h1 className="text-4xl font-black text-[#0176D3] tracking-tight">OmniLink</h1>
          <p className="text-xs text-gray-500 uppercase tracking-widest mt-1 font-semibold">Secure Loyalty CRM</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-600 uppercase mb-1">Username / Email</label>
            <input
              type="text"
              required
              placeholder="ankit.kumar@omnilink.com"
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#0176D3] text-gray-900 text-sm bg-white"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-600 uppercase mb-1">Password</label>
            <input
              type="password"
              required
              placeholder="••••••••"
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#0176D3] text-gray-900 text-sm bg-white"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-600 uppercase mb-1">Testing Context Role</label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded bg-white focus:outline-none focus:ring-2 focus:ring-[#0176D3] text-gray-900 text-sm font-medium"
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value as UserRole)}
            >
              {ROLES_LIST.map((role) => (
                <option key={role} value={role}>{role}</option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            className="w-full bg-[#0176D3] text-white py-2.5 rounded font-bold hover:bg-[#015BA7] transition duration-150 text-sm shadow-sm mt-2"
          >
            Log In
          </button>
        </form>
      </div>
    </div>
  );
};