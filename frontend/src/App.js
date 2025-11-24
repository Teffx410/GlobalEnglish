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
import OperativoDashboard from "./components/Dashboard/OperativoDashboard";
import TutorDashboard from "./components/Dashboard/TutorDashboard";

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
      </Route>

      <Route path="/operativo-dashboard" element={<OperativoDashboard />} />
      <Route path="/tutor-dashboard" element={<TutorDashboard />} />

      <Route path="*" element={<Login setToken={setToken} />} />
    </Routes>
  );
}

export default App;
