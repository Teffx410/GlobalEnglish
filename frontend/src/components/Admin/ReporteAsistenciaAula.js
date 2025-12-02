// src/components/Admin/ReporteAsistenciaAula.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

const BASE = "http://localhost:8000";

function ReporteAsistenciaAula() {
  const [instituciones, setInstituciones] = useState([]);
  const [todasAulas, setTodasAulas] = useState([]);
  const [aulasFiltradas, setAulasFiltradas] = useState([]);
  const [idInstitucion, setIdInstitucion] = useState("");
  const [idAula, setIdAula] = useState("");

  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [rows, setRows] = useState([]);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios
      .get(`${BASE}/instituciones`)
      .then((r) => setInstituciones(r.data || []))
      .catch(() => setMsg("Error al cargar instituciones."));
  }, []);

  useEffect(() => {
    axios
      .get(`${BASE}/aulas`)
      .then((r) => setTodasAulas(r.data || []))
      .catch(() => setMsg("Error al cargar aulas."));
  }, []);

  useEffect(() => {
    if (!idInstitucion) {
      setAulasFiltradas([]);
      setIdAula("");
      return;
    }
    const filtradas = (todasAulas || []).filter(
      (a) => String(a.id_institucion) === String(idInstitucion)
    );
    setAulasFiltradas(filtradas);
    setIdAula("");
  }, [idInstitucion, todasAulas]);

  const formateaFecha = (f) => (f ? String(f).slice(0, 10) : "");

  const cargarReporte = async (e) => {
    e.preventDefault();
    setMsg("");
    setRows([]);

    if (!idAula) {
      setMsg("Debes seleccionar un aula.");
      return;
    }
    if (!desde || !hasta) {
      setMsg("Debes seleccionar el rango de fechas.");
      return;
    }

    setLoading(true);
    try {
      // usa la ruta de rango; cámbiala si elegiste otro nombre
      const r = await axios.get(
        `${BASE}/reportes/aula/${idAula}/asistencia-rango`,
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
        err.response?.data?.detail || "Error al cargar el reporte de aula.";
      setMsg(detalle);
    }
    setLoading(false);
  };

  return (
    <div className="aulas-panel" style={{ maxWidth: "100%", margin: "24px 20px" }}>
      <h2 className="asistencia-title">Reporte de asistencia por aula</h2>

      <form
        className="sedes-form"
        style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 12 }}
        onSubmit={cargarReporte}
      >
        <select
          value={idInstitucion}
          onChange={(e) => {
            setIdInstitucion(e.target.value);
            setRows([]);
            setMsg("");
          }}
          className="aulas-form-input"
        >
          <option value="">Seleccione institución</option>
          {instituciones.map((inst) => (
            <option key={inst.id_institucion} value={inst.id_institucion}>
              {inst.nombre_inst}
            </option>
          ))}
        </select>

        <select
          value={idAula}
          onChange={(e) => {
            setIdAula(e.target.value);
            setRows([]);
            setMsg("");
          }}
          className="aulas-form-input"
          required
        >
          <option value="">Seleccione aula</option>
          {aulasFiltradas.map((a) => (
            <option key={a.id_aula} value={a.id_aula}>
              #{a.id_aula} - Grado {a.grado}
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
              <th>Festivo</th>
              <th>Dictada</th>
              <th>Horas dictadas</th>
              <th>Horas no dictadas</th>
              <th>Motivo inasistencia</th>
              <th>Reposición</th>
              <th>Fecha reposición</th>
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
                <td>{r.h_final}</td>
                <td>{r.es_festivo === "S" ? "Sí" : "No"}</td>
                <td>{r.dictada === "S" ? "Sí" : "No"}</td>
                <td>{r.horas_dictadas}</td>
                <td>{r.horas_no_dictadas}</td>
                <td>{r.motivo || ""}</td>
                <td>{r.reposicion === "S" ? "Sí" : "No"}</td>
                <td>{formateaFecha(r.fecha_reposicion)}</td>
              </tr>
            ))}

            {rows.length === 0 && !loading && (
              <tr>
                <td colSpan={16} style={{ textAlign: "center", padding: 10 }}>
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

export default ReporteAsistenciaAula;
