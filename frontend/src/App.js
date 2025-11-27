import React, { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Login from "./components/Auth/Login";
import AdminLayout from "./components/Dashboard/AdminLayout";
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
import MoverEstudianteAula from "./components/Admin/MoverEstudianteAula";
import Usuarios from "./components/Admin/Usuarios";
import Personas from "./components/Admin/Personas";
import HorarioTutorCalendar from "./components/Admin/HorarioTutorCalendar";
import AdminOperarComoTutor from "./components/Admin/AdminOperarComoTutor";
import AdminTomaAsistencia from "./components/Admin/AdminTomaAsistencia";
import OperativoDashboard from "./components/Dashboard/OperativoDashboard";
import TutorDashboard from "./components/Dashboard/TutorDashboard";
import AdminCalendarioPorDias from "./components/Admin/AdminCalendarioPorDias";
import AdminMotivosInasistencia from "./components/Admin/AdminMotivosInasistencia";
import AdminIngresoNotas from "./components/Admin/AdminIngresoNotas"; // NUEVO


function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");


  return (
    <Routes>
      <Route path="/" element={<Login setToken={setToken} />} />
      <Route path="/login" element={<Login setToken={setToken} />} />
      <Route path="/admin/*" element={<AdminLayout />}>
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="personas" element={<Personas />} />
        <Route path="usuarios" element={<Usuarios />} />
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
        <Route path="mover-estudiante" element={<MoverEstudianteAula />} />
        <Route path="horario-tutor-visual" element={<HorarioTutorCalendar />} />
        <Route path="operar-tutor" element={<AdminOperarComoTutor />} />
        <Route path="asistencia-aula" element={<AdminTomaAsistencia />} />
        <Route path="calendario" element={<AdminCalendarioPorDias />} />
        <Route path="motivos-inasistencia" element={<AdminMotivosInasistencia />} />
        <Route path="ingreso-notas" element={<AdminIngresoNotas />} /> {/* NUEVO */}
      </Route>
      <Route path="/operativo-dashboard" element={<OperativoDashboard />} />
      <Route path="/tutor-dashboard" element={<TutorDashboard />} />
      <Route path="*" element={<Login setToken={setToken} />} />
    </Routes>
  );
}


export default App;
