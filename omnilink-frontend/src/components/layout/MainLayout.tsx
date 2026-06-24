import type { ReactNode } from 'react';
import { useAuth } from '../../context/AuthContext';

interface MainLayoutProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  children: ReactNode;
}

export const MainLayout = ({ currentTab, setCurrentTab, children }: MainLayoutProps) => {
  const { user, logout } = useAuth();

  return (
    <div className="flex h-screen bg-[#F3F3F3] text-gray-800 font-sans antialiased overflow-hidden">
      
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col shadow-sm">
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-xl font-black text-[#0176D3]">OmniLink</h2>
          <span className="text-[10px] bg-blue-50 text-[#0176D3] font-bold px-2 py-0.5 rounded border border-blue-100 uppercase tracking-wider inline-block mt-1">
            TypeScript Matrix
          </span>
        </div>
        
        <nav className="flex-1 p-3 space-y-1">
          <button 
            onClick={() => setCurrentTab('workspace')} 
            className={`w-full text-left py-2 px-3 rounded text-sm font-semibold flex items-center space-x-2 transition ${
              currentTab === 'workspace' ? 'bg-blue-50 text-[#0176D3]' : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <span>📊 Control Dashboard</span>
          </button>
          <button 
            onClick={() => setCurrentTab('customer360')} 
            className={`w-full text-left py-2 px-3 rounded text-sm font-semibold flex items-center space-x-2 transition ${
              currentTab === 'customer360' ? 'bg-blue-50 text-[#0176D3]' : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <span>👤 Customer 360 View</span>
          </button>
        </nav>

        {/* User Card */}
        <div className="p-4 border-t border-gray-200 bg-gray-50 text-xs text-gray-500">
          <p className="font-bold text-gray-700 truncate">{user?.name}</p>
          <p className="text-[11px] truncate text-amber-700 font-semibold">{user?.role}</p>
        </div>
      </aside>

      {/* Main Panel Content Window */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6 shadow-sm">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Active Workspace:</span>
            <span className="text-xs font-bold text-gray-700 bg-gray-100 px-2 py-1 rounded border border-gray-200">
              {user?.role} Scope
            </span>
          </div>
          <button 
            onClick={logout} 
            className="text-xs font-bold text-red-600 hover:bg-red-50 border border-red-200 rounded px-3 py-1.5 transition"
          >
            Sign Out
          </button>
        </header>

        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};