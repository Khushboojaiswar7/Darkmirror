import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { Audit } from './pages/Audit';
import { Explainer } from './pages/Explainer';
import { Timeline } from './pages/Timeline';
import { Analytics } from './pages/Analytics';
import { Research } from './pages/Research';
import { Evaluation } from './pages/Evaluation';
import { Datasets } from './pages/Datasets';
import { Reports } from './pages/Reports';
import { Login } from './pages/Login';
import { useAuthStore } from './store/authStore';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

function App() {
  return (
    <BrowserRouter>
      <Toaster 
        position="top-right" 
        toastOptions={{ 
          style: { 
            background: '#1e293b', 
            color: '#f8fafc', 
            border: '1px solid #334155' 
          },
          success: { iconTheme: { primary: '#34d399', secondary: '#1e293b' } },
          error: { iconTheme: { primary: '#f43f5e', secondary: '#1e293b' } }
        }} 
      />
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="audit" element={<Audit />} />
          <Route path="explainer" element={<Explainer />} />
          <Route path="timeline/:id" element={<Timeline />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="research" element={<Research />} />
          <Route path="evaluation" element={<Evaluation />} />
          <Route path="datasets" element={<Datasets />} />
          <Route path="reports" element={<Reports />} />
        </Route>
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
