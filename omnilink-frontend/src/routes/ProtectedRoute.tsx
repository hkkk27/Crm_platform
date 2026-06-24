import { type ReactNode } from 'react';
import { useAuth } from '../context/AuthContext';
import type { UserRole } from '../types/crm';

interface ProtectedRouteProps {
  children: ReactNode;
  allowedRoles?: UserRole[];
}

export const ProtectedRoute = ({ children, allowedRoles }: ProtectedRouteProps) => {
  const { user } = useAuth();

  // 1. If the user session isn't loaded, block rendering entirely
  if (!user) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#F3F3F3] text-center p-4">
        <div className="bg-white p-6 border border-gray-200 rounded shadow-sm max-w-sm">
          <p className="text-sm font-bold text-red-600">🛑 Session Locked</p>
          <p className="text-xs text-gray-500 mt-1">Please authenticate via the secure portal gateway to access this directory path.</p>
        </div>
      </div>
    );
  }

  // 2. If the user's role isn't explicitly included in the permission criteria whitelist
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return (
      <div className="bg-red-50 border border-red-200 p-4 rounded-lg text-center max-w-xl mx-auto my-12 shadow-sm">
        <h4 className="font-bold text-red-900 text-sm">⚠️ Access Violation Warning</h4>
        <p className="text-xs text-red-700 mt-1">
          Your current context profile [{user.role}] does not possess administrative clear-box credentials to monitor this dashboard segment.
        </p>
      </div>
    );
  }

  // 3. Otherwise, clean execution pathway passes execution forward
  return <>{children}</>;
};