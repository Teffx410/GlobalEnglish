// src/App.js
import React, { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/Auth/Login";
import AdminLayout from "./components/Dashboard/AdminLayout";
import TutorLayout from "./components/Dashboard/TutorLayout";

import AdminDashboard from "./components/Dashboard/AdminDashboard";
import Instituciones from "./components/Admin/Instituciones";
import Sedes from "./components/Admin/Sedes";
import Aulas from "./components/Admin/Aulas";
import Horarios from "./components/Admin/Horarios";
import AsignarHorarioAula from "./components/Admin/AsignarHorarioAula";
import AsignarTutorAula from "./components/Admin/AsignarTutorAula";
import Periodos from "./components/Admin/Periodos";
import Componentes from "./components/Admin/Componentes";
import Estudiantes from "./components/Admin/Estudiantes";
import AsignarAula from "./components/Admin/AsignarAula";
import Usuarios from "./components/Admin/Usuarios";
import Personas from "./components/Admin/Personas";
import HorarioTutorCalendar from "./components/Admin/HorarioTutorCalendar";
import TomaDeAsistenciaEstudiante from "./components/Admin/TomaDeAsistenciaEstudiante";
import AdminTomaAsistencia from "./components/Admin/AdminTomaAsistencia";
import OperativoDashboard from "./components/Dashboard/OperativoDashboard";
import AdminCalendarioPorDias from "./components/Admin/AdminCalendarioPorDias";
import AdminMotivosInasistencia from "./components/Admin/AdminMotivosInasistencia";
import AdminIngresoNotas from "./components/Admin/AdminIngresoNotas";
import AdminVerificarAsistenciaTutor from "./components/Admin/AdminVerificarAsistenciaTutor";
import AdminScoreEstudiante from "./components/Admin/AdminScoreEstudiante";
import AdminAutogestionTutorReporte from "./components/Admin/AdminAutogestionTutorReporte";
import AdminFestivos from "./components/Admin/AdminFestivos";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");

  const rol = localStorage.getItem("rol") || "SIN_ROL";
  const esAdmin = rol === "ADMINISTRADOR";
  const esAdministrativo = rol === "ADMINISTRATIVO";
  const esTutor = rol === "TUTOR";

  const requireAuth = element =>
    token ? element : <Navigate to="/login" replace />;

  return (
    <Routes>
      {/* Login */}
      <Route path="/" element={<Login setToken={setToken} />} />
      <Route path="/login" element={<Login setToken={setToken} />} />

      {/* ADMIN / ADMINISTRATIVO */}
      <Route path="/admin/*" element={requireAuth(<AdminLayout />)}>
        <Route path="dashboard" element={<AdminDashboard />} />

        {(esAdministrativo || esAdmin) && (
          <>
            <Route path="personas" element={<Personas />} />
            <Route path="instituciones" element={<Instituciones />} />
            <Route path="sedes" element={<Sedes />} />
            <Route path="aulas" element={<Aulas />} />
            <Route path="horarios" element={<Horarios />} />
            <Route path="asignar-horario" element={<AsignarHorarioAula />} />
            <Route path="asignar-tutor" element={<AsignarTutorAula />} />
            <Route path="periodos" element={<Periodos />} />
            <Route path="componentes" element={<Componentes />} />
            <Route path="estudiantes" element={<Estudiantes />} />
            <Route path="asignar-aula" element={<AsignarAula />} />
            <Route
              path="motivos-inasistencia"
              element={<AdminMotivosInasistencia />}
            />
            <Route
              path="score-estudiante"
              element={<AdminScoreEstudiante />}
            />
            <Route
              path="verificar-asistencia-tutor"
              element={<AdminVerificarAsistenciaTutor />}
            />
          </>
        )}

        {esAdministrativo && (
          <Route path="festivos" element={<AdminFestivos />} />
        )}

        {esAdmin && (
          <>
            <Route path="usuarios" element={<Usuarios />} />
            <Route path="calendario" element={<AdminCalendarioPorDias />} />
          </>
        )}

        {(esTutor || esAdministrativo || esAdmin) && (
          <>
            <Route path="ingreso-notas" element={<AdminIngresoNotas />} />
            <Route
              path="toma-asistencia-estudiante"
              element={<TomaDeAsistenciaEstudiante />}
            />
            <Route path="asistencia-aula" element={<AdminTomaAsistencia />} />
            <Route
              path="horario-tutor-visual"
              element={<HorarioTutorCalendar />}
            />
            <Route
              path="reporte-autogestion-tutor"
              element={<AdminAutogestionTutorReporte />}
            />
          </>
        )}
      </Route>

      {/* TUTOR (prefijo /tutor) */}
      <Route path="/tutor/*" element={requireAuth(<TutorLayout />)}>
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="ingreso-notas" element={<AdminIngresoNotas />} />
        <Route
          path="toma-asistencia-estudiante"
          element={<TomaDeAsistenciaEstudiante />}
        />
        <Route path="asistencia-aula" element={<AdminTomaAsistencia />} />
        <Route
          path="horario-tutor-visual"
          element={<HorarioTutorCalendar />}
        />
        <Route
          path="reporte-autogestion-tutor"
          element={<AdminAutogestionTutorReporte />}
        />
      </Route>

      {/* Opcional: dashboards antiguos */}
      <Route
        path="/operativo-dashboard"
        element={requireAuth(<OperativoDashboard />)}
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;
