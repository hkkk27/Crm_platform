import { createContext, useState, useContext, type ReactNode } from 'react';
import type { UserRole, UserSession } from '../types/crm';

interface AuthContextType {
  user: UserSession | null;
  login: (username: string, chosenRole: UserRole) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserSession | null>(null);

  const login = (username: string, chosenRole: UserRole) => {
    setUser({
      name: 'Ankit Kumar',
      role: chosenRole,
      email: username || 'ankit@omnilink.local'
    });
  };

  const logout = () => {
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside an AuthProvider');
  }
  return context;
};