import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./presentation/pages/LoginPage";
import DocenteHomePage from "./presentation/pages/docente/DocenteHomePage";
import StatsPage from "./presentation/pages/StatsPage"; // si lo usas aún
import ProfilePage from "./presentation/pages/ProfilePage";
import SettingsPage from "./presentation/pages/SettingsPage";
import EventsPage from "./presentation/pages/EventsPage";
import AdminUsersPage from "./presentation/pages/admin/AdminUsersPage";
import AdminHomePage from "./presentation/pages/admin/AdminHomePage";
import StudentSchedulePage from "./presentation/pages/student/StudentSchedulePage";

import { AuthProvider } from "./app/providers/AuthProvider";
import PrivateRoute from "./presentation/routes/PrivateRoute";
import PublicRoute from "./presentation/routes/PublicRoute";
import RoleRoute from "./presentation/routes/RoleRoute";
import AdminRestriccionesPage from "./presentation/pages/admin/AdminRestriccionesPage";

import DocenteRestrictionsPage from "./presentation/pages/docente/DocenteRestrictionsPage";
import StudentHomePage from "./presentation/pages/student/StudentHomePage";
import StudentEventsPlaceholderPage from "./presentation/pages/student/StudentEventsPlaceholderPage";
import UnauthorizedPage from "./presentation/pages/UnauthorizedPage";

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Redirección inicial */}
          <Route path="/" element={<Navigate to="/login" replace />} />

          {/* Público */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />

          {/* No autorizado */}
          <Route path="/unauthorized" element={<UnauthorizedPage />} />

          {/* Docente */}
          <Route
            path="/home"
            element={
              <PrivateRoute>
                <RoleRoute allowed={["docente"]}>
                  <DocenteHomePage />
                </RoleRoute>
              </PrivateRoute>
            }
          />
          <Route
            path="/student/home"
            element={
              <PrivateRoute>
                <RoleRoute allowed={["estudiante"]}>
                  <StudentHomePage />
                </RoleRoute>
              </PrivateRoute>
            }
          />
          <Route
            path="/restrictions"
            element={
              <PrivateRoute>
                <RoleRoute allowed={["docente"]}>
                  <DocenteRestrictionsPage />
                </RoleRoute>
              </PrivateRoute>
            }
          />
          <Route
            path="/events"
            element={
              <PrivateRoute>
                <RoleRoute allowed={["docente"]}>
                  <EventsPage />
                </RoleRoute>
              </PrivateRoute>
            }
          />
          <Route
            path="/student/events"
            element={
              <PrivateRoute>
                <RoleRoute allowed={["estudiante"]}>
                  <StudentEventsPlaceholderPage />
                </RoleRoute>
              </PrivateRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <PrivateRoute>
                <RoleRoute allowed={["docente", "admin", "estudiante"]}>
                  <SettingsPage />
                </RoleRoute>
              </PrivateRoute>
            }
          />
          <Route
            path="/schedule"
            element={
              <PrivateRoute>
                <RoleRoute allowed={["docente", "estudiante"]}>
                  <StudentSchedulePage />
                </RoleRoute>
              </PrivateRoute>
            }
          />

          {/* Si aún tienes estas: protégelas por rol que corresponda o elimínalas */}
          <Route
            path="/stats"
            element={
              <PrivateRoute>
                <RoleRoute allowed={["docente"]}>
                  <StatsPage />
                </RoleRoute>
              </PrivateRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <RoleRoute allowed={["docente"]}>
                  <ProfilePage />
                </RoleRoute>
              </PrivateRoute>
            }
          />

          <Route
            path="/admin"
            element={
              <PrivateRoute>
                <RoleRoute allowed={["admin"]}>
                  <AdminHomePage />
                </RoleRoute>
              </PrivateRoute>
            }
          />
          {/* Administrador */}
          <Route
            path="/admin/users"
            element={
              <PrivateRoute>
                <RoleRoute allowed={["admin"]}>
                  <AdminUsersPage />
                </RoleRoute>
              </PrivateRoute>
            }
          />
            <Route
          path="/admin/restricciones"
          element={
            <PrivateRoute>
              <RoleRoute allowed={["admin"]}>
                <AdminRestriccionesPage />
              </RoleRoute>
            </PrivateRoute>
          }
        />


          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
