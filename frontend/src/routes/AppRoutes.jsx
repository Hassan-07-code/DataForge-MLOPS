import { BrowserRouter, Routes, Route } from "react-router-dom";

import MainLayout from "../components/layout/MainLayout";

import LandingPage from "../pages/landing/LandingPage";
import DashboardPage from "../pages/dashboard/DashboardPage";
import DataPage from "../pages/data/DataPage";
import DataCleaningPage from "../pages/cleaning/DataCleaningPage";
import VisualizationPage from "../pages/visualization/VisualizationPage";
import TrainingPage from "../pages/training/TrainingPage";
import ExperimentsPage from "../pages/experiments/ExperimentsPage";
import ModelsPage from "../pages/models/ModelsPage";
import PredictionsPage from "../pages/predictions/PredictionsPage";
import ReportsPage from "../pages/reports/ReportsPage";
import SettingsPage from "../pages/settings/SettingsPage";
import NotFoundPage from "../pages/not-found/NotFoundPage";

function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Landing */}
        <Route path="/" element={<LandingPage />} />

        {/* Dashboard Main Layout */}
        <Route element={<MainLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/data" element={<DataPage />} />
          <Route path="/cleaning" element={<DataCleaningPage />} />
          <Route path="/visualization" element={<VisualizationPage />} />
          <Route path="/training" element={<TrainingPage />} />
          <Route path="/experiments" element={<ExperimentsPage />} />
          <Route path="/models" element={<ModelsPage />} />
          <Route path="/predictions" element={<PredictionsPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        {/* 404 Not Found */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default AppRoutes;