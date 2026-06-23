import { useState } from 'react';

// 1. Core State & Infrastructure Engine Imports
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';

// 2. Functional Interface Component View Imports
import { LoginPage } from './pages/auth/LoginPage';
import { MainLayout } from './components/layout/MainLayout';
import { Customer360 } from './pages/customer/Customer360';

/**
 * AppContent controls the primary frontend view filtering layout switch.
 * It listens to the global AuthContext session tracking data framework layer.
 */
const AppContent = () => {
  const { user } = useAuth();
  const [currentTab, setCurrentTab] = useState<string>('workspace');

  // Security Wall: If nobody is logged in, force render the authorization portal entry window!
  if (!user) {
    return <LoginPage />;
  }

  // Active Session Layout: Once credentials match, mount the persistent navigation framework frame
  return (
    <MainLayout currentTab={currentTab} setCurrentTab={setCurrentTab}>
      {currentTab === 'customer360' && <Customer360 />}
    </MainLayout>
  );
};

/**
 * Root Orchestrator Wrapper
 * Embeds global app states and system toast banners into the frontend runtime memory.
 */
export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </AuthProvider>
  );
}