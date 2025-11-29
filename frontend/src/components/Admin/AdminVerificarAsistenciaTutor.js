import React, { useEffect, useState } from "react";
import axios from "axios";

const BASE = "http://localhost:8000";

function AdminVerificarAsistenciaTutor() {
  const [tutores, setTutores] = useState([]);
  const [tutorSel, setTutorSel] = useState("");
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [filas, setFilas] = useState([]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    axios
      .get(`${BASE}/admin/listar-tutores`)
      .then(r => setTutores(r.data || []))
      .catch(() => setMsg("Error al cargar tutores."));
  }, []);

  const cargarReporte = async () => {
    if (!tutorSel || !desde || !hasta) {
      setMsg("Seleccione tutor y rango de fechas.");
      return;
    }
    setMsg("");
    try {
      const r = await axios.get(`${BASE}/admin/reporte-asistencia-tutor`, {
        params: {
          id_persona: tutorSel,
          fecha_inicio: desde,
          fecha_fin: hasta,
        },
      });
      setFilas(r.data || []);
    } catch (e) {
      setMsg("Error al cargar reporte de asistencia del tutor.");
      setFilas([]);
    }
  };

  return (
    <div className="aulas-panel" style={{ maxWidth: "100%", margin: "24px 20px" }}>
      <h2 style={{ marginBottom: 18 }}>Verificar asistencia del tutor</h2>

      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 16 }}>
        <label>
          <b>Tutor:</b>
          <select
            className="aulas-form-input"
            value={tutorSel}
            onChange={e => setTutorSel(e.target.value)}
            style={{ marginLeft: 8, minWidth: 180 }}
          >
            <option value="">Seleccione tutor</option>
            {tutores.map(t => (
              <option key={t.id_persona} value={t.id_persona}>
                {t.nombre}
              </option>
            ))}
          </select>
        </label>

        <label>
          Desde:
          <input
            type="date"
            className="aulas-form-input"
            value={desde}
            onChange={e => setDesde(e.target.value)}
            style={{ marginLeft: 8 }}
          />
        </label>

        <label>
          Hasta:
          <input
            type="date"
            className="aulas-form-input"
            value={hasta}
            onChange={e => setHasta(e.target.value)}
            style={{ marginLeft: 8 }}
          />
        </label>

        <button className="aulas-btn" type="button" onClick={cargarReporte}>
          Buscar
        </button>
      </div>

      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Día</th>
              <th>Aula</th>
              <th>Hora inicio</th>
              <th>Hora fin</th>
              <th>Dictada</th>
              <th>Horas</th>
              <th>Reposición</th>
              <th>Fecha reposición</th>
            </tr>
          </thead>
          <tbody>
            {filas.map((f, i) => (
              <tr key={i}>
                <td>{f.fecha_clase}</td>
                <td>{f.dia_semana}</td>
                <td>{f.id_aula}</td>
                <td>{f.hora_inicio}</td>
                <td>{f.hora_fin}</td>
                <td>{f.dictada === "S" ? "Sí" : "No"}</td>
                <td>{f.horas_dictadas}</td>
                <td>{f.reposicion === "S" ? "Sí" : "No"}</td>
                <td>{f.fecha_reposicion || "-"}</td>
              </tr>
            ))}
            {filas.length === 0 && (
              <tr>
                <td colSpan={9} style={{ textAlign: "center", padding: 12 }}>
                  Sin registros en el rango seleccionado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {msg && (
        <div
          style={{
            marginTop: 16,
            padding: "10px 14px",
            borderRadius: 6,
            border: msg.startsWith("Error")
              ? "1px solid #fecaca"
              : "1px solid #bbf7d0",
            background: msg.startsWith("Error") ? "#fef2f2" : "#ecfdf3",
            color: msg.startsWith("Error") ? "#b91c1c" : "#166534",
            fontWeight: 500,
          }}
        >
          {msg}
        </div>
      )}
    </div>
  );
}

export default AdminVerificarAsistenciaTutor;
