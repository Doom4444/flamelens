import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { Investigations } from './pages/Investigations';
import { InvestigationDetails } from './pages/InvestigationDetails';
import { Files } from './pages/Files';
import { Storage } from './pages/Storage';
import { Comparison } from './pages/Comparison';
import { Assistant } from './pages/Assistant';
import { NotFound } from './pages/NotFound';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/overview" replace />} />
          <Route path="overview" element={<Dashboard />} />
          <Route path="investigations" element={<Investigations />} />
          <Route path="investigations/:id" element={<InvestigationDetails />} />
          <Route path="files" element={<Files />} />
          <Route path="storage" element={<Storage />} />
          <Route path="comparison" element={<Comparison />} />
          <Route path="assistant" element={<Assistant />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
