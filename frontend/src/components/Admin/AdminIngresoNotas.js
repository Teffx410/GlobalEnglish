// src/components/Admin/AdminIngresoNotas.js
import React, { useState, useEffect } from "react";
import axios from "axios";

const BASE = "http://localhost:8000";

// Mapea grado de aula -> tipo de programa usado en COMPONENTE.tipo_programa
function inferTipoPrograma(grado) {
  const g = parseInt(grado, 10);
  if ([4, 5].includes(g)) return "INSIDECLASSROOM";
  if ([9, 10].includes(g)) return "OUTSIDECLASSROOM";
  return null;
}

function AdminIngresoNotas() {
  const rol = localStorage.getItem("rol");
  const esSoloTutor = rol === "TUTOR";
  const idPersonaSesion = localStorage.getItem("id_persona") || "";

  const [tutores, setTutores] = useState([]);
  const [aulas, setAulas] = useState([]);
  const [estudiantes, setEstudiantes] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [componentes, setComponentes] = useState([]);

  const [tutorSel, setTutorSel] = useState(esSoloTutor ? idPersonaSesion : "");
  const [aulaSel, setAulaSel] = useState("");
  const [gradoAulaSel, setGradoAulaSel] = useState(null);
  const [periodoSel, setPeriodoSel] = useState("");
  const [tipoProgramaActual, setTipoProgramaActual] = useState(null);

  const [tabActiva, setTabActiva] = useState("notas"); // "notas" | "resumen"
  const [componenteActivoId, setComponenteActivoId] = useState(null);

  // notas[ id_componente ][ id_estudiante ] = valor
  const [notas, setNotas] = useState({});
  const [msg, setMsg] = useState("");
  const [cargando, setCargando] = useState(false);
  const [guardando, setGuardando] = useState(false);

  // Cargar tutores (solo admin/adminstrativo) y períodos al montar
  useEffect(() => {
    if (!esSoloTutor) {
      axios
        .get(`${BASE}/admin/listar-tutores`)
        .then(res => setTutores(res.data || []));
    }
    axios
      .get(`${BASE}/admin/listar-periodos`)
      .then(res => setPeriodos(res.data || []));
  }, [esSoloTutor]);

  // Si es tutor, cargar sus aulas automáticamente
  useEffect(() => {
    if (!esSoloTutor) return;
    const inicial = idPersonaSesion;
    if (inicial) {
      handleTutorChange(inicial);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [esSoloTutor, idPersonaSesion]);

  // Cambiar tutor
  const handleTutorChange = async val => {
    setTutorSel(val);
    setAulaSel("");
    setGradoAulaSel(null);
    setEstudiantes([]);
    setPeriodoSel("");
    setComponentes([]);
    setTipoProgramaActual(null);
    setComponenteActivoId(null);
    setNotas({});
    if (!val) {
      setAulas([]);
      return;
    }
    try {
      const res = await axios.get(
        `${BASE}/admin/listar-aulas-tutor?id_persona=${val}`
      );
      setAulas(res.data || []);
    } catch (e) {
      console.error("Error listando aulas del tutor:", e);
      setAulas([]);
    }
  };

  // Cambiar aula
  const handleAulaChange = async val => {
    setAulaSel(val);
    setEstudiantes([]);
    setPeriodoSel("");
    setComponentes([]);
    setComponenteActivoId(null);
    setNotas({});

    if (!val) {
      setGradoAulaSel(null);
      setTipoProgramaActual(null);
      return;
    }

    const aulaObj = aulas.find(a => String(a.id_aula) === String(val));
    const grado = aulaObj ? aulaObj.grado : null;
    setGradoAulaSel(grado);

    const tipo = inferTipoPrograma(grado);
    setTipoProgramaActual(tipo);

    try {
      const res = await axios.get(
        `${BASE}/admin/listar-estudiantes-aula?id_aula=${val}`
      );
      setEstudiantes(res.data || []);
    } catch (e) {
      console.error("Error listando estudiantes del aula:", e);
      setEstudiantes([]);
    }
    // componentes se cargarán cuando se elija periodo
  };

  // Cargar componentes por período + tipo_programa
  const cargarComponentes = async (id_periodo, tipo_programa) => {
    setComponentes([]);
    setComponenteActivoId(null);
    setNotas({});
    if (!id_periodo || !tipo_programa) return;
    try {
      const res = await axios.get(
        `${BASE}/admin/listar-componentes-periodo-tipo?id_periodo=${id_periodo}&tipo_programa=${tipo_programa}`
      );
      const comps = res.data || [];
      setComponentes(comps);
      if (comps.length > 0) {
        setComponenteActivoId(comps[0].id_componente);
        await cargarNotasComponente(comps[0].id_componente, comps, estudiantes);
      }
    } catch (e) {
      console.error("Error listando componentes:", e);
      setComponentes([]);
    }
  };

  // Cambiar período
  const handlePeriodoChange = async val => {
    setPeriodoSel(val);
    setComponentes([]);
    setComponenteActivoId(null);
    setNotas({});
    if (!val) return;
    if (tipoProgramaActual) {
      await cargarComponentes(val, tipoProgramaActual);
    }
  };

  // Cargar notas de un componente para todos los estudiantes
  const cargarNotasComponente = async (
    id_componente,
    comps = componentes,
    ests = estudiantes
  ) => {
    if (!id_componente || ests.length === 0) return;
    setCargando(true);
    try {
      const nuevasNotasComp = {};
      for (const est of ests) {
        const res = await axios.get(
          `${BASE}/admin/obtener-nota-estudiante?id_estudiante=${est.id_estudiante}&id_componente=${id_componente}`
        );
        nuevasNotasComp[est.id_estudiante] =
          res.data.nota !== null && res.data.nota !== undefined
            ? res.data.nota
            : "";
      }
      setNotas(prev => ({
        ...prev,
        [id_componente]: {
          ...(prev[id_componente] || {}),
          ...nuevasNotasComp,
        },
      }));
    } catch (e) {
      console.error("Error cargando notas:", e);
    }
    setCargando(false);
  };

  // Cambiar pestaña de componente
  const handleComponenteTab = async id_componente => {
    setTabActiva("notas");
    setComponenteActivoId(id_componente);
    if (!notas[id_componente]) {
      await cargarNotasComponente(id_componente);
    }
  };

  // Cambiar nota (solo en memoria)
  const handleNotaChange = (id_componente, id_est, valor) => {
    setNotas(prev => ({
      ...prev,
      [id_componente]: {
        ...(prev[id_componente] || {}),
        [id_est]: valor,
      },
    }));
  };

  // Guardar TODAS las notas del componente activo
  const handleGuardarTodas = async () => {
    if (!componenteActivoId || estudiantes.length === 0) return;
    setMsg("");
    setGuardando(true);
    try {
      const notasComp = notas[componenteActivoId] || {};
      const peticiones = [];

      for (const est of estudiantes) {
        const val = notasComp[est.id_estudiante];
        if (val === "" || val === undefined) continue;
        const n = parseFloat(val);
        if (isNaN(n) || n < 0 || n > 5) {
          setMsg("Hay notas inválidas. Verifica que todas estén entre 0 y 5.");
          setGuardando(false);
          return;
        }
        peticiones.push(
          axios.post(`${BASE}/admin/registrar-nota-estudiante`, {
            id_estudiante: est.id_estudiante,
            id_componente: componenteActivoId,
            nota: n,
          })
        );
      }

      await Promise.all(peticiones);
      setMsg("Notas guardadas correctamente.");
      setTimeout(() => setMsg(""), 2000);
      await cargarNotasComponente(componenteActivoId);
    } catch (e) {
      console.error("Error al guardar notas:", e);
      setMsg(
        "Error al guardar notas: " + (e.response?.data?.detail || e.message)
      );
    }
    setGuardando(false);
  };

  // Cálculo de resumen
  const calcularResumen = () => {
    if (estudiantes.length === 0 || componentes.length === 0) return [];
    const resumen = [];

    for (const est of estudiantes) {
      let totalPonderado = 0;
      let totalPorcentaje = 0;
      const notasEst = {};

      for (const comp of componentes) {
        const n = notas[comp.id_componente]?.[est.id_estudiante];
        const valor = n === "" || n === undefined ? null : parseFloat(n);
        notasEst[comp.id_componente] = valor;

        if (valor !== null && !isNaN(valor)) {
          totalPonderado += valor * (comp.porcentaje / 100);
          totalPorcentaje += comp.porcentaje;
        }
      }

      const definitiva =
        totalPorcentaje > 0 ? parseFloat(totalPonderado.toFixed(2)) : null;

      resumen.push({
        estudiante: est,
        notasEst,
        definitiva,
      });
    }

    return resumen;
  };

  const resumenDatos = calcularResumen();

  return (
    <div className="aulas-panel" style={{ maxWidth: "100%", margin: "24px 20px" }}>
      <h2 style={{ margin: "0 0 20px" }}>
        {esSoloTutor ? "Ingreso de mis notas" : "Ingreso de notas"}
      </h2>

      {/* Filtros superiores */}
      <div style={{ marginBottom: 14 }}>
        {!esSoloTutor && (
          <div style={{ marginBottom: 10 }}>
            <label
              style={{ fontWeight: "bold", display: "inline-block", minWidth: 110 }}
            >
              Tutor:
            </label>
            <select
              value={tutorSel}
              onChange={e => handleTutorChange(e.target.value)}
              className="aulas-form-input"
              style={{ maxWidth: 320 }}
            >
              <option value="">Seleccione tutor</option>
              {tutores.map(t => (
                <option value={t.id_persona} key={t.id_persona}>
                  {t.nombre}
                </option>
              ))}
            </select>
          </div>
        )}

        {aulas.length > 0 && (
          <div style={{ marginBottom: 10 }}>
            <label
              style={{ fontWeight: "bold", display: "inline-block", minWidth: 110 }}
            >
              Aula:
            </label>
            <select
              value={aulaSel}
              onChange={e => handleAulaChange(e.target.value)}
              className="aulas-form-input"
              style={{ maxWidth: 320 }}
            >
              <option value="">Seleccione aula</option>
              {aulas.map(a => (
                <option value={a.id_aula} key={a.id_aula}>
                  Grado {a.grado} (Aula {a.id_aula})
                </option>
              ))}
            </select>
          </div>
        )}

        {estudiantes.length > 0 && (
          <div style={{ marginBottom: 10 }}>
            <label
              style={{ fontWeight: "bold", display: "inline-block", minWidth: 110 }}
            >
              Período:
            </label>
            <select
              value={periodoSel}
              onChange={e => handlePeriodoChange(e.target.value)}
              className="aulas-form-input"
              style={{ maxWidth: 320 }}
            >
              <option value="">Seleccione período</option>
              {periodos.map(p => (
                <option value={p.id_periodo} key={p.id_periodo}>
                  {p.nombre}
                </option>
              ))}
            </select>
          </div>
        )}

        {gradoAulaSel && (
          <div style={{ marginBottom: 4, color: "#6b7280", fontSize: "0.9em" }}>
            Tipo de programa detectado por grado {gradoAulaSel}:{" "}
            <b>{tipoProgramaActual || "N/A"}</b>
          </div>
        )}
      </div>

      {/* Tabs componentes + resumen */}
      {componentes.length > 0 && (
        <div className="notas-tabs">
          {componentes.map(c => (
            <button
              key={c.id_componente}
              type="button"
              onClick={() => handleComponenteTab(c.id_componente)}
              className={
                "notas-tab" +
                (tabActiva === "notas" && componenteActivoId === c.id_componente
                  ? " active"
                  : "")
              }
            >
              {c.nombre} ({c.porcentaje}%)
            </button>
          ))}
          <button
            type="button"
            onClick={() => setTabActiva("resumen")}
            className={
              "notas-tab notas-tab-resumen" +
              (tabActiva === "resumen" ? " active" : "")
            }
          >
            Resumen
          </button>
        </div>
      )}

      {msg && (
        <div
          style={{
            marginBottom: 16,
            padding: 12,
            background: msg.toLowerCase().includes("error") ? "#ffefef" : "#eaffea",
            borderRadius: 8,
            color: msg.toLowerCase().includes("error") ? "#a11" : "#237327",
            border: msg.toLowerCase().includes("error")
              ? "1px solid #fcc"
              : "1px solid #afd",
            fontWeight: 500,
          }}
        >
          {msg}
        </div>
      )}

      {/* TAB NOTAS */}
      {tabActiva === "notas" &&
        componenteActivoId &&
        estudiantes.length > 0 && (
          <div style={{ marginTop: 10 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 10,
              }}
            >
              <h4 style={{ margin: 0 }}>Ingresar notas</h4>
              <button
                type="button"
                className="aulas-btn"
                onClick={handleGuardarTodas}
                disabled={guardando || cargando}
                style={{ minWidth: 150, height: "auto" }}
              >
                {guardando ? "Guardando..." : "Guardar todas"}
              </button>
            </div>

            {cargando && (
              <div
                style={{
                  color: "#666",
                  textAlign: "center",
                  padding: "20px",
                }}
              >
                ⏳ Cargando notas...
              </div>
            )}

            {!cargando && (
              <div style={{ overflowX: "auto" }}>
                <table
                  style={{
                    width: "100%",
                    borderCollapse: "collapse",
                    background: "#fff",
                    borderRadius: 12,
                    overflow: "hidden",
                  }}
                >
                  <thead>
                    <tr style={{ background: "#f8fafe" }}>
                      <th
                        style={{
                          padding: 12,
                          textAlign: "left",
                          borderBottom: "2px solid #e2e8f0",
                          fontWeight: "bold",
                          color: "#2563eb",
                        }}
                      >
                        Estudiante
                      </th>
                      <th
                        style={{
                          padding: 12,
                          textAlign: "center",
                          borderBottom: "2px solid #e2e8f0",
                          fontWeight: "bold",
                          color: "#2563eb",
                        }}
                      >
                        Nota (0–5)
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {estudiantes.map((e, idx) => (
                      <tr
                        key={e.id_estudiante}
                        style={{
                          borderBottom: "1px solid #edf2f7",
                          background: idx % 2 === 0 ? "#f9fafb" : "#ffffff",
                        }}
                      >
                        <td style={{ padding: 12 }}>
                          {e.nombres} {e.apellidos}
                        </td>
                        <td style={{ padding: 12, textAlign: "center" }}>
                          <input
                            type="number"
                            min="0"
                            max="5"
                            step="0.1"
                            value={
                              (notas[componenteActivoId] || {})[
                                e.id_estudiante
                              ] ?? ""
                            }
                            onChange={evt =>
                              handleNotaChange(
                                componenteActivoId,
                                e.id_estudiante,
                                evt.target.value
                              )
                            }
                            style={{
                              width: 80,
                              padding: "6px 8px",
                              border: "1px solid #cbd5e0",
                              borderRadius: 6,
                              textAlign: "center",
                              background: "#f7fafc",
                            }}
                            placeholder="0.0"
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

      {/* TAB RESUMEN */}
      {tabActiva === "resumen" && estudiantes.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <h4 style={{ marginBottom: 12 }}>Resumen de notas</h4>
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                background: "#fff",
                borderRadius: 12,
                overflow: "hidden",
              }}
            >
              <thead>
                <tr style={{ background: "#f8fafe" }}>
                  <th
                    style={{
                      padding: 12,
                      textAlign: "left",
                      borderBottom: "2px solid #e2e8f0",
                      fontWeight: "bold",
                      color: "#2563eb",
                    }}
                  >
                    Estudiante
                  </th>
                  {componentes.map(c => (
                    <th
                      key={c.id_componente}
                      style={{
                        padding: 12,
                        textAlign: "center",
                        borderBottom: "2px solid #e2e8f0",
                        fontWeight: "bold",
                        color: "#2563eb",
                      }}
                    >
                      {c.nombre}
                    </th>
                  ))}
                  <th
                    style={{
                      padding: 12,
                      textAlign: "center",
                      borderBottom: "2px solid #e2e8f0",
                      fontWeight: "bold",
                      color: "#2563eb",
                    }}
                  >
                    Definitiva
                  </th>
                </tr>
              </thead>
              <tbody>
                {resumenDatos.map((row, idx) => (
                  <tr
                    key={row.estudiante.id_estudiante}
                    style={{
                      borderBottom: "1px solid #edf2f7",
                      background: idx % 2 === 0 ? "#f9fafb" : "#ffffff",
                    }}
                  >
                    <td style={{ padding: 12 }}>
                      {row.estudiante.nombres} {row.estudiante.apellidos}
                    </td>
                    {componentes.map(c => {
                      const v = row.notasEst[c.id_componente];
                      return (
                        <td
                          key={c.id_componente}
                          style={{ padding: 12, textAlign: "center" }}
                        >
                          {v !== null && !isNaN(v) ? v.toFixed(1) : "-"}
                        </td>
                      );
                    })}
                    <td style={{ padding: 12, textAlign: "center" }}>
                      {row.definitiva !== null && !isNaN(row.definitiva)
                        ? row.definitiva.toFixed(2)
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminIngresoNotas;
