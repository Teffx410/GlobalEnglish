// src/App.js
import React, { useState } from "react";
import { Routes, Route } from "react-router-dom";

// Importa tus componentes
import Login from "./components/Auth/Login";
import AdminDashboard from "./components/Dashboard/AdminDashboard";
import OperativoDashboard from "./components/Dashboard/OperativoDashboard";
import TutorDashboard from "./components/Dashboard/TutorDashboard";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");

  return (
    <Routes>
      <Route path="/" element={<Login setToken={setToken} />} />
      <Route path="/login" element={<Login setToken={setToken} />} />
      <Route path="/admin-dashboard" element={<AdminDashboard />} />
      <Route path="/operativo-dashboard" element={<OperativoDashboard />} />
      <Route path="/tutor-dashboard" element={<TutorDashboard />} />
      <Route path="*" element={<Login setToken={setToken} />} />
    </Routes>
  );
}

export default App;
