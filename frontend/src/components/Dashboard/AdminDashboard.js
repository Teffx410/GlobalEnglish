// src/components/Dashboard/AdminDashboard.js
import React from "react";
import { BsHouse, BsPeople, BsCalendar, BsClipboardData, BsFillBarChartLineFill } from "react-icons/bs";
import "../../styles/AdminDashboard.css";

// KPIs y actividad pueden luego venir desde el backend
const kpis = [
  { label: "Instituciones", value: 12, icon: <BsHouse size={32} /> },
  { label: "Aulas Activas", value: 48, icon: <BsClipboardData size={32} /> },
  { label: "Estudiantes", value: 450, icon: <BsPeople size={32} /> },
  { label: "Asistencia Promedio", value: "92%", icon: <BsFillBarChartLineFill size={32} /> },
];

const actividadReciente = [
  { texto: "Se agregó un nuevo aula en IED Central", tiempo: "Hace 2 horas" },
  { texto: "Registro de asistencia completado", tiempo: "Hace 4 horas" },
  { texto: "Nuevo estudiante inscrito en 4º grado", tiempo: "Hace 6 horas" },
];

function AdminDashboard() {
  // Obtén el usuario desde localStorage
  const nombre = localStorage.getItem("nombre_user") || "Sin nombre";
  const rol = localStorage.getItem("rol") || "Sin rol";

  return (
    <div className="admin-dashboard-content">
      <header>
        <h2>¡Bienvenido, {nombre}!</h2>
        <div>Rol: {rol}</div>
      </header>
      <section className="admin-kpis">
        {kpis.map((kpi, idx) => (
          <div key={idx} className="admin-kpi-card">
            <div className="kpi-icon">{kpi.icon}</div>
            <div className="kpi-label">{kpi.label}</div>
            <div className="kpi-value">{kpi.value}</div>
          </div>
        ))}
      </section>
      <section className="admin-activity">
        <h3>Actividad Reciente</h3>
        <ul>
          {actividadReciente.map((act, idx) => (
            <li key={idx}>
              {act.texto} <span className="actividad-tiempo">{act.tiempo}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default AdminDashboard;
