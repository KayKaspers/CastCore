import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import BackupPage from "./pages/BackupPage";
import ChannelsPage from "./pages/ChannelsPage";
import DashboardPage from "./pages/DashboardPage";
import DocsPage from "./pages/DocsPage";
import LoginPage from "./pages/LoginPage";
import MediaLibraryPage from "./pages/MediaLibraryPage";
import MonitoringPage from "./pages/MonitoringPage";
import NotificationsPage from "./pages/NotificationsPage";
import PlaylistsPage from "./pages/PlaylistsPage";
import RecordingsPage from "./pages/RecordingsPage";
import ResourcesPage from "./pages/ResourcesPage";
import SchedulerPage from "./pages/SchedulerPage";
import SetupWizardPage from "./pages/SetupWizardPage";
import SourcesPage from "./pages/SourcesPage";
import StreamJobsPage from "./pages/StreamJobsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<DashboardPage />} />
        <Route path="/streams" element={<StreamJobsPage />} />
        <Route path="/channels" element={<ChannelsPage />} />
        <Route path="/sources" element={<SourcesPage />} />
        <Route path="/media" element={<MediaLibraryPage />} />
        <Route path="/playlists" element={<PlaylistsPage />} />
        <Route path="/monitoring" element={<MonitoringPage />} />
        <Route path="/recordings" element={<RecordingsPage />} />
        <Route path="/scheduler" element={<SchedulerPage />} />
        <Route path="/resources" element={<ResourcesPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/backup" element={<BackupPage />} />
        <Route path="/docs" element={<DocsPage />} />
        <Route path="/setup" element={<SetupWizardPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
