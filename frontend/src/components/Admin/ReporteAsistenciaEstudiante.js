// src/components/Admin/ReporteAsistenciaEstudiante.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

const BASE = "http://localhost:8000";

function ReporteAsistenciaEstudiante() {
  const [estudiantes, setEstudiantes] = useState([]);
  const [idEstudiante, setIdEstudiante] = useState("");

  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [rows, setRows] = useState([]);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios
      .get(`${BASE}/estudiantes`)
      .then((r) => setEstudiantes(r.data || []))
      .catch(() => setMsg("Error al cargar estudiantes."));
  }, []);

  const formateaFecha = (f) => (f ? String(f).slice(0, 10) : "");

  const cargarReporte = async (e) => {
    e.preventDefault();
    setMsg("");
    setRows([]);

    if (!idEstudiante) {
      setMsg("Debes seleccionar un estudiante.");
      return;
    }
    if (!desde || !hasta) {
      setMsg("Debes seleccionar el rango de fechas.");
      return;
    }

    setLoading(true);
    try {
      const r = await axios.get(
        `${BASE}/reportes/estudiante/${idEstudiante}/asistencia-rango`,
        { params: { fecha_inicio: desde, fecha_fin: hasta } }
      );
      const items = Array.isArray(r.data) ? r.data : r.data?.items || [];
      setRows(items);
      if (items.length === 0) {
        setMsg("No hay registros de asistencia para los filtros seleccionados.");
      }
    } catch (err) {
      console.error(err);
      const detalle =
        err.response?.data?.detail || "Error al cargar el reporte del estudiante.";
      setMsg(detalle);
    }
    setLoading(false);
  };

  return (
    <div className="aulas-panel" style={{ maxWidth: "100%", margin: "24px 20px" }}>
      <h2 className="asistencia-title">Reporte de asistencia por estudiante</h2>

      <form
        className="sedes-form"
        style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 12 }}
        onSubmit={cargarReporte}
      >
        <select
          value={idEstudiante}
          onChange={(e) => {
            setIdEstudiante(e.target.value);
            setRows([]);
            setMsg("");
          }}
          className="aulas-form-input"
        >
          <option value="">Seleccione estudiante</option>
          {estudiantes.map((e) => (
            <option key={e.id_estudiante} value={e.id_estudiante}>
              {e.apellidos} {e.nombres}
            </option>
          ))}
        </select>

        <input
          type="date"
          className="aulas-form-input"
          value={desde}
          onChange={(e) => setDesde(e.target.value)}
        />
        <input
          type="date"
          className="aulas-form-input"
          value={hasta}
          onChange={(e) => setHasta(e.target.value)}
        />

        <button type="submit" className="aulas-btn" disabled={loading}>
          {loading ? "Buscando..." : "Buscar"}
        </button>
      </form>

      {msg && (
        <div
          style={{
            marginTop: 4,
            marginBottom: 8,
            padding: "8px 12px",
            background: "#e9f5ff",
            borderRadius: 4,
            color: "#064b7f",
          }}
        >
          {msg}
        </div>
      )}

      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Semana</th>
              <th>Institución</th>
              <th>Aula</th>
              <th>Grado</th>
              <th>Tutor</th>
              <th>Día</th>
              <th>Hora inicio</th>
              <th>Hora fin</th>
              <th>Asistió</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, idx) => (
              <tr key={idx}>
                <td>{formateaFecha(r.fecha_clase)}</td>
                <td>{r.numero_semana ?? ""}</td>
                <td>{r.nombre_inst}</td>
                <td>{r.id_aula}</td>
                <td>{r.grado || ""}</td>
                <td>{r.tutor || ""}</td>
                <td>{r.dia_semana}</td>
                <td>{r.hora_inicio}</td>
                <td>{r.hora_fin}</td>
                <td>{r.asistio === "S" ? "Sí" : "No"}</td>
              </tr>
            ))}

            {rows.length === 0 && !loading && (
              <tr>
                <td colSpan={10} style={{ textAlign: "center", padding: 10 }}>
                  Sin datos para mostrar.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ReporteAsistenciaEstudiante;
