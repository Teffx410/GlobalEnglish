// src/components/Admin/BoletinEstudiante.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

const BASE = "http://localhost:8000";

function BoletinEstudiante() {
  const [estudiantes, setEstudiantes] = useState([]);
  const [periodos, setPeriodos] = useState([]);

  const [idEstudiante, setIdEstudiante] = useState("");
  const [idPeriodo, setIdPeriodo] = useState("");      // 1..4 o "FINAL"

  const [data, setData] = useState(null);             // boletín del periodo seleccionado o final
  const [promedios, setPromedios] = useState(null);   // definitivas por periodo + acumulado
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios
      .get(`${BASE}/estudiantes`)
      .then((r) => setEstudiantes(r.data || []))
      .catch(() => setMsg("Error al cargar estudiantes."));

    axios
      .get(`${BASE}/periodos`)
      .then((r) => setPeriodos(r.data || []))
      .catch(() => setMsg("Error al cargar periodos."));
  }, []);

  const getNombreEstudiante = () => {
    const est = estudiantes.find((e) => String(e.id_estudiante) === String(idEstudiante));
    if (!est) return "";
    return `${est.apellidos} ${est.nombres}`;
  };

  const cargarBoletin = async (e) => {
    e.preventDefault();
    setMsg("");
    setData(null);
    setPromedios(null);

    if (!idEstudiante) {
      setMsg("Debes seleccionar un estudiante.");
      return;
    }
    if (!idPeriodo) {
      setMsg("Debes seleccionar un periodo o Boletín final.");
      return;
    }

    // Boletín final (acumulado)
    if (idPeriodo === "FINAL") {
      setLoading(true);
      try {
        const idsPeriodos = periodos.map((p) => p.id_periodo).slice(0, 4);
        const respuestas = await Promise.all(
          idsPeriodos.map((pid) =>
            axios.get(
              `${BASE}/reportes/estudiante/${idEstudiante}/boletin/${pid}`
            )
          )
        );
        const boletines = respuestas.map((r) => r.data || {});
        const definitivas = boletines.map((b) => b.definitiva).filter((d) => d != null);
        const promedioAcumulado =
          definitivas.length > 0
            ? Number(
                (
                  definitivas.reduce((acc, v) => acc + Number(v || 0), 0) /
                  definitivas.length
                ).toFixed(2)
              )
            : null;

        const resumenPeriodos = boletines.map((b, idx) => ({
          id_periodo: idsPeriodos[idx],
          nombre_periodo: b.periodo || `Periodo ${idx + 1}`,
          definitiva: b.definitiva != null ? Number(b.definitiva).toFixed(2) : "-",
        }));

        const ref = boletines[0] || {};
        setData({
          ...ref,
          periodo: "Boletín final (acumulado)",
          componentes: [],
          definitiva: promedioAcumulado,
        });
        setPromedios({
          periodos: resumenPeriodos,
          acumulado: promedioAcumulado,
        });
        if (definitivas.length === 0) {
          setMsg("No hay definitivas registradas en los periodos para este estudiante.");
        }
      } catch (err) {
        console.error(err);
        const detalle =
          err.response?.data?.detail || "Error al cargar el boletín final.";
        setMsg(detalle);
      }
      setLoading(false);
      return;
    }

    // Boletín de un periodo
    setLoading(true);
    try {
      const r = await axios.get(
        `${BASE}/reportes/estudiante/${idEstudiante}/boletin/${idPeriodo}`
      );
      const bd = r.data;
      setData(bd);
      setPromedios(null);
      if (!bd || !bd.componentes || bd.componentes.length === 0) {
        setMsg("No hay notas registradas para ese estudiante en el periodo.");
      }
    } catch (err) {
      console.error(err);
      const detalle =
        err.response?.data?.detail || "Error al cargar el boletín del estudiante.";
      setMsg(detalle);
    }
    setLoading(false);
  };

  return (
    <div className="aulas-panel" style={{ maxWidth: "100%", margin: "24px 20px" }}>
      <h2 className="asistencia-title">Boletín de calificaciones</h2>

      <form
        className="sedes-form"
        style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 12 }}
        onSubmit={cargarBoletin}
      >
        <select
          value={idEstudiante}
          onChange={(e) => {
            setIdEstudiante(e.target.value);
            setData(null);
            setPromedios(null);
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

        <select
          value={idPeriodo}
          onChange={(e) => {
            setIdPeriodo(e.target.value);
            setData(null);
            setPromedios(null);
            setMsg("");
          }}
          className="aulas-form-input"
        >
          <option value="">Seleccione periodo</option>
          {periodos.map((p) => (
            <option key={p.id_periodo} value={p.id_periodo}>
              {p.nombre}
            </option>
          ))}
          <option value="FINAL">Boletín final (acumulado)</option>
        </select>

        <button type="submit" className="aulas-btn" disabled={loading}>
          {loading ? "Cargando..." : "Generar boletín"}
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

      {data && (
        <div style={{ marginTop: 12 }}>
          {/* Encabezado del boletín */}
          <div
            style={{
              padding: "12px 16px",
              border: "1px solid #ddd",
              borderRadius: 4,
              marginBottom: 12,
              background: "#fafafa",
            }}
          >
            <h3 style={{ margin: "0 0 8px 0" }}>{data.institucion || "Sin institución"}</h3>
            <p style={{ margin: "2px 0" }}>
              <strong>Estudiante:</strong> {getNombreEstudiante()}
            </p>
            <p style={{ margin: "2px 0" }}>
              <strong>Grado:</strong> {data.grado || "-"}
            </p>
            <p style={{ margin: "2px 0" }}>
              <strong>Periodo:</strong> {data.periodo || "-"}
            </p>
          </div>

          {/* Tabla de componentes con fila de definitiva */}
          {data.componentes && data.componentes.length > 0 && (
            <div className="table-responsive">
              <table className="aulas-table">
                <thead>
                  <tr>
                    <th>Componente</th>
                    <th>Porcentaje</th>
                    <th>Nota</th>
                  </tr>
                </thead>
                <tbody>
                  {data.componentes.map((c) => (
                    <tr key={c.id_componente}>
                      <td>{c.nombre}</td>
                      <td>{c.porcentaje != null ? `${c.porcentaje}%` : "-"}</td>
                      <td>{c.nota != null ? Number(c.nota).toFixed(2) : "-"}</td>
                    </tr>
                  ))}
                  <tr>
                    <td colSpan={2} style={{ textAlign: "right", fontWeight: "bold" }}>
                      Nota definitiva del periodo
                    </td>
                    <td style={{ fontWeight: "bold" }}>
                      {data.definitiva != null ? Number(data.definitiva).toFixed(2) : "-"}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {/* Resumen de promedios por periodo + acumulado (solo para FINAL) */}
          {promedios && (
            <div style={{ marginTop: 16 }}>
              <h4 style={{ marginBottom: 8 }}>Promedios por periodo</h4>
              <div className="table-responsive">
                <table className="aulas-table">
                  <thead>
                    <tr>
                      <th>Periodo</th>
                      <th>Nota definitiva</th>
                    </tr>
                  </thead>
                  <tbody>
                    {promedios.periodos.map((p) => (
                      <tr key={p.id_periodo}>
                        <td>{p.nombre_periodo}</td>
                        <td>{p.definitiva}</td>
                      </tr>
                    ))}
                    <tr>
                      <td style={{ textAlign: "right", fontWeight: "bold" }}>
                        Promedio acumulado
                      </td>
                      <td style={{ fontWeight: "bold" }}>
                        {promedios.acumulado != null
                          ? Number(promedios.acumulado).toFixed(2)
                          : "-"}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default BoletinEstudiante;
