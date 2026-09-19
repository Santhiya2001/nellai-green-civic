import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Privacy from "./pages/Privacy";
import Terms from "./pages/Terms";

import CitizenDashboard from "./pages/citizen/Dashboard";
import ReportIssue from "./pages/citizen/ReportIssue";
import MyComplaints from "./pages/citizen/MyComplaints";
import NearbyIssues from "./pages/citizen/NearbyIssues";
import EnvironmentalMap from "./pages/citizen/EnvironmentalMap";
import VolunteerActivities from "./pages/citizen/VolunteerActivities";
import Notifications from "./pages/citizen/Notifications";

import AdminDashboard from "./pages/admin/Dashboard";
import ComplaintManagement from "./pages/admin/ComplaintManagement";
import Authorities from "./pages/admin/Authorities";
import EscalationManagement from "./pages/admin/EscalationManagement";
import ModuleManagement from "./pages/admin/ModuleManagement";
import GISMap from "./pages/admin/GISMap";

import AssignedComplaints from "./pages/authority/AssignedComplaints";
import Performance from "./pages/authority/Performance";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/terms" element={<Terms />} />

      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="citizen" element={<CitizenDashboard />} />
        <Route path="citizen/report" element={<ReportIssue />} />
        <Route path="citizen/complaints" element={<MyComplaints />} />
        <Route path="citizen/nearby" element={<NearbyIssues />} />
        <Route path="citizen/map" element={<EnvironmentalMap />} />
        <Route path="citizen/volunteer" element={<VolunteerActivities />} />
        <Route path="citizen/notifications" element={<Notifications />} />

        <Route
          path="admin"
          element={
            <ProtectedRoute roles={["ADMIN", "SUPER_ADMIN"]}>
              <AdminDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/complaints"
          element={
            <ProtectedRoute roles={["ADMIN", "SUPER_ADMIN"]}>
              <ComplaintManagement />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/authorities"
          element={
            <ProtectedRoute roles={["ADMIN", "SUPER_ADMIN"]}>
              <Authorities />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/escalation"
          element={
            <ProtectedRoute roles={["ADMIN", "SUPER_ADMIN"]}>
              <EscalationManagement />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/modules"
          element={
            <ProtectedRoute roles={["ADMIN", "SUPER_ADMIN"]}>
              <ModuleManagement />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin/map"
          element={
            <ProtectedRoute roles={["ADMIN", "SUPER_ADMIN"]}>
              <GISMap />
            </ProtectedRoute>
          }
        />

        <Route
          path="authority"
          element={
            <ProtectedRoute roles={["AUTHORITY"]}>
              <AssignedComplaints />
            </ProtectedRoute>
          }
        />
        <Route
          path="authority/performance"
          element={
            <ProtectedRoute roles={["AUTHORITY"]}>
              <Performance />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
