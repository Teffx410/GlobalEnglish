import React, { useState } from "react";
import { Routes, Route } from "react-router-dom";

// Importa todos tus componentes
import Login from "./components/Auth/Login";
import AdminLayout from "./components/Dashboard/AdminLayout";
import AdminDashboard from "./components/Dashboard/AdminDashboard";
import Instituciones from "./components/Admin/Instituciones";
import Sedes from "./components/Admin/Sedes"; // Importa el componente de sedes
import OperativoDashboard from "./components/Dashboard/OperativoDashboard";
import TutorDashboard from "./components/Dashboard/TutorDashboard";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");

  return (
    <Routes>
      <Route path="/" element={<Login setToken={setToken} />} />
      <Route path="/login" element={<Login setToken={setToken} />} />

      {/* Layout general bajo /admin */}
      <Route path="/admin/*" element={<AdminLayout />}>
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="instituciones" element={<Instituciones />} />
        <Route path="sedes" element={<Sedes />} /> {/* CRUD sedes */}
        {/* Puedes agregar más rutas administrativas aquí */}
      </Route>

      {/* Otros paneles independientes */}
      <Route path="/operativo-dashboard" element={<OperativoDashboard />} />
      <Route path="/tutor-dashboard" element={<TutorDashboard />} />

      {/* Fallback: va al login si no encuentra la ruta */}
      <Route path="*" element={<Login setToken={setToken} />} />
    </Routes>
  );
}

export default App;
