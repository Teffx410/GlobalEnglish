// src/components/Dashboard/AdminDashboard.js
import React, { useEffect, useState } from "react";
import {
  BsHouse,
  BsPeople,
  BsClipboardData,
  BsFillBarChartLineFill,
} from "react-icons/bs";
import axios from "axios";
import "../../styles/AdminDashboard.css";

const BASE = "http://localhost:8000";

function AdminDashboard() {
  const nombre = localStorage.getItem("nombre_user") || "Sin nombre";
  const rol = localStorage.getItem("rol") || "SIN_ROL";
  const idPersona = localStorage.getItem("id_persona") || "";

  const esTutor = rol === "TUTOR";

  const [kpis, setKpis] = useState({
    instituciones: 0,
    aulas_activas: 0,
    estudiantes: 0,
    asistencia_promedio: 0,
  });
  const [actividadReciente, setActividadReciente] = useState([]);
  const [loadingKpis, setLoadingKpis] = useState(true);
  const [loadingAct, setLoadingAct] = useState(true);
  const [errorKpis, setErrorKpis] = useState("");
  const [errorAct, setErrorAct] = useState("");

  // KPIs
  useEffect(() => {
    const fetchKpis = async () => {
      try {
        setLoadingKpis(true);
        setErrorKpis("");

        const params = {};
        if (esTutor && idPersona) {
          params.id_persona = idPersona;
          params.rol = "TUTOR";
        }

        const resp = await axios.get(`${BASE}/admin/dashboard-kpis`, {
          params,
        });
        setKpis(resp.data || {});
      } catch (err) {
        console.error("Error cargando KPIs:", err);
        setErrorKpis("No se pudieron cargar los indicadores.");
      } finally {
        setLoadingKpis(false);
      }
    };

    fetchKpis();
  }, [esTutor, idPersona]);

  // Actividad reciente
  useEffect(() => {
    const fetchActividad = async () => {
      try {
        setLoadingAct(true);
        setErrorAct("");

        const params = {};
        if (esTutor && idPersona) {
          params.id_persona = idPersona;
          params.rol = "TUTOR";
        }

        const resp = await axios.get(`${BASE}/admin/dashboard-actividad`, {
          params,
        });
        // backend devuelve [{texto, hace}], adaptamos a {texto, tiempo}
        const lista = (resp.data || []).map(a => ({
          texto: a.texto,
          tiempo: a.hace,
        }));
        setActividadReciente(lista);
      } catch (err) {
        console.error("Error cargando actividad:", err);
        setErrorAct("No se pudo cargar la actividad reciente.");
      } finally {
        setLoadingAct(false);
      }
    };

    fetchActividad();
  }, [esTutor, idPersona]);

  const cards = [
    {
      key: "instituciones",
      label: "Instituciones",
      value: kpis.instituciones,
      icon: <BsHouse size={32} />,
      visible: !esTutor,
    },
    {
      key: "aulas_activas",
      label: "Aulas Activas",
      value: kpis.aulas_activas,
      icon: <BsClipboardData size={32} />,
      visible: true,
    },
    {
      key: "estudiantes",
      label: "Estudiantes",
      value: kpis.estudiantes,
      icon: <BsPeople size={32} />,
      visible: true,
    },
    {
      key: "asistencia_promedio",
      label: "Asistencia Promedio",
      value: `${kpis.asistencia_promedio || 0}%`,
      icon: <BsFillBarChartLineFill size={32} />,
      visible: true,
    },
  ].filter(c => c.visible);

  return (
    <div className="admin-dashboard-content">
      <header>
        <h2>¡Bienvenido, {nombre}!</h2>
        <div>Rol: {rol}</div>
      </header>

      {errorKpis && (
        <div
          style={{
            marginTop: 10,
            marginBottom: 10,
            padding: "8px 12px",
            borderRadius: 6,
            background: "#fef2f2",
            color: "#b91c1c",
            border: "1px solid #fecaca",
          }}
        >
          {errorKpis}
        </div>
      )}

      <section className="admin-kpis">
        {loadingKpis ? (
          <div>Cargando indicadores...</div>
        ) : (
          cards.map(card => (
            <div key={card.key} className="admin-kpi-card">
              <div className="kpi-icon">{card.icon}</div>
              <div className="kpi-label">{card.label}</div>
              <div className="kpi-value">{card.value}</div>
            </div>
          ))
        )}
      </section>

      <section className="admin-activity">
        <h3>Actividad Reciente</h3>

        {errorAct && (
          <div
            style={{
              marginBottom: 10,
              padding: "8px 12px",
              borderRadius: 6,
              background: "#fef2f2",
              color: "#b91c1c",
              border: "1px solid #fecaca",
            }}
          >
            {errorAct}
          </div>
        )}

        {loadingAct ? (
          <div>Cargando actividad...</div>
        ) : actividadReciente.length === 0 ? (
          <div style={{ color: "#6b7280" }}>Sin registros recientes.</div>
        ) : (
          <ul>
            {actividadReciente.map((act, idx) => (
              <li key={idx}>
                {act.texto}{" "}
                <span className="actividad-tiempo">{act.tiempo}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default AdminDashboard;
