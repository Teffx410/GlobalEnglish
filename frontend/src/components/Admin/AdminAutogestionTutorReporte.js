// src/components/Admin/AdminAutogestionTutorReporte.js
import React, { useEffect, useState } from "react";
import axios from "axios";

const BASE = "http://localhost:8000";

function AdminAutogestionTutorReporte() {
  const [tutores, setTutores] = useState([]);
  const [tutorSel, setTutorSel] = useState("");

  const [tabActiva, setTabActiva] = useState("ASISTENCIA"); // "ASISTENCIA" | "NOTAS"

  // Asistencia
  const [desde, setDesde] = useState("");
  const [hasta, setHasta] = useState("");
  const [asistencia, setAsistencia] = useState([]);
  const [loadingAsis, setLoadingAsis] = useState(false);

  // Notas
  const [periodos, setPeriodos] = useState([]);
  const [periodoSel, setPeriodoSel] = useState("");
  const [aulasNotas, setAulasNotas] = useState([]);       // tabs de aula
  const [aulaNotasSel, setAulaNotasSel] = useState("");   // id_aula activo
  const [notas, setNotas] = useState([]);                 // [{id_estudiante,...,componentes:[],definitiva}]
  const [loadingNotas, setLoadingNotas] = useState(false);

  const [msg, setMsg] = useState("");

  useEffect(() => {
    axios
      .get(`${BASE}/admin/listar-tutores`)
      .then(r => setTutores(r.data || []))
      .catch(() => setMsg("Error al cargar tutores."));

    axios
      .get(`${BASE}/admin/periodos`)
      .then(r => setPeriodos(r.data || []))
      .catch(() => setMsg("Error al cargar periodos."));
  }, []);

  // Cuando cambia el tutor, limpiar datos de notas
  useEffect(() => {
    setAulasNotas([]);
    setAulaNotasSel("");
    setNotas([]);
  }, [tutorSel]);

  const cargarAsistencia = async () => {
    if (!tutorSel) {
      setMsg("Seleccione un tutor.");
      return;
    }
    if (!desde || !hasta) {
      setMsg("Seleccione el rango de fechas.");
      return;
    }
    setLoadingAsis(true);
    setMsg("");
    try {
      const r = await axios.get(`${BASE}/reporte/autogestion-tutor`, {
        params: {
          id_persona: tutorSel,
          fecha_inicio: desde,
          fecha_fin: hasta,
        },
      });
      setAsistencia(r.data.asistencia || []);
    } catch (e) {
      console.error(e);
      setMsg("Error al cargar reporte de asistencia.");
      setAsistencia([]);
    }
    setLoadingAsis(false);
  };

  const cargarAulasNotas = async () => {
    if (!tutorSel) {
      setMsg("Seleccione un tutor.");
      return;
    }
    try {
      const r = await axios.get(`${BASE}/admin/aulas-por-tutor`, {
        params: { id_persona: tutorSel },
      });
      const lista = r.data || [];
      setAulasNotas(lista);
      if (lista.length > 0) {
        setAulaNotasSel(String(lista[0].id_aula));
      } else {
        setAulaNotasSel("");
      }
    } catch (e) {
      console.error(e);
      setMsg("Error al cargar aulas del tutor.");
      setAulasNotas([]);
      setAulaNotasSel("");
    }
  };

  // Cargar aulas al entrar a la pestaña NOTAS
  useEffect(() => {
    if (tabActiva === "NOTAS" && tutorSel) {
      cargarAulasNotas();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tabActiva, tutorSel]);

  const cargarNotas = async () => {
    if (!tutorSel) {
      setMsg("Seleccione un tutor.");
      return;
    }
    if (!periodoSel) {
      setMsg("Seleccione un periodo.");
      return;
    }
    if (!aulaNotasSel) {
      setMsg("Seleccione un aula.");
      return;
    }
    setLoadingNotas(true);
    setMsg("");
    try {
      const r = await axios.get(`${BASE}/reporte/notas-tutor-periodo`, {
        params: {
          id_persona: tutorSel,
          id_periodo: periodoSel,
          id_aula: aulaNotasSel,
        },
      });
      setNotas(r.data || []);
    } catch (e) {
      console.error(e);
      setMsg("Error al cargar notas del tutor.");
      setNotas([]);
    }
    setLoadingNotas(false);
  };

  return (
    <div className="aulas-panel" style={{ maxWidth: "100%", margin: "24px 20px" }}>
      <h2 style={{ marginBottom: 18 }}>Reporte de asistencia y notas por tutor</h2>

      {/* Tutor */}
      <div
        style={{
          display: "flex",
          gap: 16,
          flexWrap: "wrap",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <label>
          <b>Tutor:</b>
          <select
            className="aulas-form-input"
            value={tutorSel}
            onChange={e => setTutorSel(e.target.value)}
            style={{ marginLeft: 8, minWidth: 220 }}
          >
            <option value="">Seleccione tutor</option>
            {tutores.map(t => (
              <option key={t.id_persona} value={t.id_persona}>
                {t.nombre}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* Tabs principales */}
      <div
        style={{
          display: "flex",
          gap: 8,
          borderBottom: "1px solid #e5e7eb",
          marginBottom: 16,
          paddingBottom: 4,
        }}
      >
        <button
          type="button"
          onClick={() => setTabActiva("ASISTENCIA")}
          style={{
            padding: "6px 16px",
            borderRadius: 999,
            border:
              tabActiva === "ASISTENCIA" ? "2px solid #2563eb" : "1px solid #d1d5db",
            background: tabActiva === "ASISTENCIA" ? "#eff6ff" : "#ffffff",
            color: tabActiva === "ASISTENCIA" ? "#1d4ed8" : "#374151",
            cursor: "pointer",
            fontWeight: 500,
          }}
        >
          Asistencia
        </button>
        <button
          type="button"
          onClick={() => setTabActiva("NOTAS")}
          style={{
            padding: "6px 16px",
            borderRadius: 999,
            border:
              tabActiva === "NOTAS" ? "2px solid #2563eb" : "1px solid #d1d5db",
            background: tabActiva === "NOTAS" ? "#eff6ff" : "#ffffff",
            color: tabActiva === "NOTAS" ? "#1d4ed8" : "#374151",
            cursor: "pointer",
            fontWeight: 500,
          }}
        >
          Notas por periodo
        </button>
      </div>

      {/* TAB ASISTENCIA */}
      {tabActiva === "ASISTENCIA" && (
        <>
          <div
            style={{
              display: "flex",
              gap: 16,
              flexWrap: "wrap",
              alignItems: "center",
              marginBottom: 16,
            }}
          >
            <label>
              Desde:
              <input
                type="date"
                className="aulas-form-input"
                style={{ marginLeft: 8 }}
                value={desde}
                onChange={e => setDesde(e.target.value)}
              />
            </label>
            <label>
              Hasta:
              <input
                type="date"
                className="aulas-form-input"
                style={{ marginLeft: 8 }}
                value={hasta}
                onChange={e => setHasta(e.target.value)}
              />
            </label>
            <button
              className="aulas-btn"
              type="button"
              onClick={cargarAsistencia}
              disabled={loadingAsis}
            >
              {loadingAsis ? "Buscando..." : "Buscar"}
            </button>
          </div>

          <h3 style={{ marginTop: 10, marginBottom: 8 }}>Asistencia por clase</h3>
          <div className="table-responsive">
            <table className="aulas-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Aula</th>
                  <th>Grado</th>
                  <th>Hora inicio</th>
                  <th>Hora fin</th>
                  <th>Dictada</th>
                  <th>Horas</th>
                  <th>% asistencia</th>
                </tr>
              </thead>
              <tbody>
                {asistencia.map((a, i) => (
                  <tr key={i}>
                    <td>{a.fecha_clase}</td>
                    <td>{a.id_aula}</td>
                    <td>{a.grado}</td>
                    <td>{a.hora_inicio}</td>
                    <td>{a.hora_fin}</td>
                    <td>{a.dictada === "S" ? "Sí" : "No"}</td>
                    <td>{a.horas_dictadas}</td>
                    <td>{a.pct_asistencia}%</td>
                  </tr>
                ))}
                {asistencia.length === 0 && (
                  <tr>
                    <td colSpan={8} style={{ textAlign: "center", padding: 10 }}>
                      Sin registros en el rango seleccionado.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* TAB NOTAS */}
      {tabActiva === "NOTAS" && (
        <>
          {/* Filtros de periodo y botón buscar */}
          <div
            style={{
              display: "flex",
              gap: 16,
              flexWrap: "wrap",
              alignItems: "center",
              marginBottom: 12,
            }}
          >
            <label>
              Periodo:
              <select
                className="aulas-form-input"
                value={periodoSel}
                onChange={e => setPeriodoSel(e.target.value)}
                style={{ marginLeft: 8, minWidth: 220 }}
              >
                <option value="">Seleccione periodo</option>
                {periodos.map(p => (
                  <option key={p.id_periodo} value={p.id_periodo}>
                    {p.nombre}
                  </option>
                ))}
              </select>
            </label>
            <button
              className="aulas-btn"
              type="button"
              onClick={cargarNotas}
              disabled={loadingNotas}
            >
              {loadingNotas ? "Buscando..." : "Buscar"}
            </button>
          </div>

          {/* Tabs de aulas */}
          {aulasNotas.length > 0 && (
            <div
              style={{
                display: "flex",
                gap: 8,
                flexWrap: "wrap",
                marginBottom: 12,
                borderBottom: "1px solid #e5e7eb",
                paddingBottom: 4,
              }}
            >
              {aulasNotas.map(a => (
                <button
                  key={a.id_aula}
                  type="button"
                  onClick={() => {
                    setAulaNotasSel(String(a.id_aula));
                    setNotas([]);
                  }}
                  style={{
                    padding: "4px 12px",
                    borderRadius: 999,
                    border:
                      String(aulaNotasSel) === String(a.id_aula)
                        ? "2px solid #2563eb"
                        : "1px solid #d1d5db",
                    background:
                      String(aulaNotasSel) === String(a.id_aula)
                        ? "#eff6ff"
                        : "#ffffff",
                    color:
                      String(aulaNotasSel) === String(a.id_aula)
                        ? "#1d4ed8"
                        : "#374151",
                    cursor: "pointer",
                    fontSize: ".85rem",
                    fontWeight: 500,
                  }}
                >
                  Aula {a.id_aula} • {a.grado}
                </button>
              ))}
            </div>
          )}

          {/* Tabla de notas (solo lectura) */}
          <div className="table-responsive">
            <table className="aulas-table">
              <thead>
                <tr>
                  <th>Estudiante</th>
                  {notas[0]?.componentes?.map(c => (
                    <th key={c.id_componente} style={{ textAlign: "center" }}>
                      {c.nombre_componente}
                    </th>
                  )) || (
                    <th style={{ textAlign: "center" }}>Componentes</th>
                  )}
                  <th style={{ textAlign: "center" }}>Definitiva</th>
                </tr>
              </thead>
              <tbody>
                {notas.map(est => (
                  <tr key={est.id_estudiante}>
                    <td>
                      {est.nombres} {est.apellidos}
                    </td>
                    {est.componentes.map(c => (
                      <td key={c.id_componente} style={{ textAlign: "center" }}>
                        {c.nota !== null && c.nota !== undefined ? c.nota : "-"}
                      </td>
                    ))}
                    <td style={{ textAlign: "center", fontWeight: 600 }}>
                      {est.definitiva !== null && est.definitiva !== undefined
                        ? est.definitiva
                        : "-"}
                    </td>
                  </tr>
                ))}
                {notas.length === 0 && (
                  <tr>
                    <td
                      colSpan={
                        (notas[0]?.componentes?.length || 0) + 2
                      }
                      style={{ textAlign: "center", padding: 10 }}
                    >
                      Sin notas para el periodo seleccionado.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

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

export default AdminAutogestionTutorReporte;
