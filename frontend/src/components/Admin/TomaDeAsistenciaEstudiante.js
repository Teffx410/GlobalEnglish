// src/components/TomaDeAsistenciaEstudiante.js
import React, { useState, useEffect } from "react";
import axios from "axios";

const BASE = "http://localhost:8000";

function TomaDeAsistenciaEstudiante() {
  const [tutores, setTutores] = useState([]);
  const [clases, setClases] = useState([]);
  const [tutorSel, setTutorSel] = useState("");
  const [tabActiva, setTabActiva] = useState("TODAS");
  const [estudiantes, setEstudiantes] = useState([]);
  const [marcas, setMarcas] = useState({});
  const [historialPlano, setHistorialPlano] = useState([]);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios
      .get(`${BASE}/admin/listar-tutores`)
      .then(res => setTutores(res.data || []))
      .catch(() => setMsg("Error al cargar tutores."));
  }, []);

  const cargarClases = async id_persona => {
    setClases([]);
    setTabActiva("TODAS");
    setEstudiantes([]);
    setMarcas({});
    setHistorialPlano([]);
    setMsg("");
    if (!id_persona) return;

    try {
      const r = await axios.get(`${BASE}/admin/listar-clases-tutor`, {
        params: { id_persona },
      });
      const listaClases = r.data || [];
      setClases(listaClases);

      const rHist = await axios.get(
        `${BASE}/admin/listar-asistencia-estudiantes-todas`,
        { params: { id_persona } }
      );
      setHistorialPlano(rHist.data || []);
    } catch {
      setMsg("Error al cargar información del tutor.");
    }
  };

  const cargarEstudiantes = async id_asist => {
    setEstudiantes([]);
    setMarcas({});
    setMsg("");
    if (!id_asist || id_asist === "TODAS") return;
    try {
      const resp = await axios.get(
        `${BASE}/admin/listar-asistencia-estudiantes`,
        { params: { id_asist } }
      );
      const lista = resp.data || [];
      setEstudiantes(lista);
      const inicial = {};
      lista.forEach(e => {
        inicial[e.id_estudiante] = e.asistio === "S" ? "S" : "N";
      });
      setMarcas(inicial);
    } catch {
      setMsg("Error al cargar asistencia de estudiantes.");
    }
  };

  const cambiarTab = id_asist => {
    setTabActiva(id_asist);
    if (id_asist === "TODAS") {
      setEstudiantes([]);
      setMarcas({});
    } else {
      cargarEstudiantes(id_asist);
    }
  };

  const toggleAsistencia = id_est => {
    setMarcas(prev => ({
      ...prev,
      [id_est]: prev[id_est] === "S" ? "N" : "S",
    }));
    setMsg("");
  };

  const guardarTodas = async () => {
    if (!tabActiva || tabActiva === "TODAS" || estudiantes.length === 0) return;
    setLoading(true);
    setMsg("");
    try {
      const peticiones = estudiantes.map(e =>
        axios.post(`${BASE}/admin/registrar-asistencia-estudiante`, {
          id_asist: parseInt(tabActiva),
          id_estudiante: e.id_estudiante,
          asistio: marcas[e.id_estudiante] || "N",
        })
      );
      await Promise.all(peticiones);

      setMsg("Asistencia de todos los estudiantes guardada correctamente.");

      await cargarEstudiantes(tabActiva);

      if (tutorSel) {
        const rHist = await axios.get(
          `${BASE}/admin/listar-asistencia-estudiantes-todas`,
          { params: { id_persona: tutorSel } }
        );
        setHistorialPlano(rHist.data || []);
      }
    } catch (err) {
      const detalle =
        err.response?.data?.detail || "Error al guardar asistencia.";
      setMsg("Error: " + detalle);
    }
    setLoading(false);
  };

  const clasesOrdenadas = [...clases].sort((a, b) =>
    String(a.fecha_clase).localeCompare(String(b.fecha_clase))
  );

  const mapaClasesPorId = {};
  clasesOrdenadas.forEach((c, idx) => {
    mapaClasesPorId[c.id_asist] = { index: idx, ...c };
  });

  const resumenPorEstudiante = {};
  if (tabActiva === "TODAS" && historialPlano.length > 0) {
    historialPlano.forEach(r => {
      const idEst = r.id_estudiante;
      if (!resumenPorEstudiante[idEst]) {
        resumenPorEstudiante[idEst] = {
          id_estudiante: idEst,
          nombres: r.nombres,
          apellidos: r.apellidos,
          asistencias: Array(clasesOrdenadas.length).fill(""),
        };
      }
      const infoClase = mapaClasesPorId[r.id_asist];
      if (infoClase) {
        resumenPorEstudiante[idEst].asistencias[infoClase.index] =
          r.asistio === "S" ? "S" : "N";
      }
    });
  }

  const filasResumen = Object.values(resumenPorEstudiante);

  const Circulo = ({ lleno }) => (
    <span
      style={{
        display: "inline-block",
        width: 16,
        height: 16,
        borderRadius: "999px",
        border: lleno ? "2px solid #16a34a" : "2px solid #d1d5db",
        background: lleno ? "#bbf7d0" : "#ffffff",
      }}
    />
  );

  return (
    <div className="aulas-panel" style={{ maxWidth: "100%", margin: "24px 20px" }}>
      <h2 style={{ marginBottom: 18 }}>Toma de asistencia (estudiantes)</h2>

      <div
        style={{
          display: "flex",
          gap: 18,
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
            onChange={e => {
              const v = e.target.value;
              setTutorSel(v);
              cargarClases(v);
            }}
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
      </div>

      {clases.length > 0 && (
        <div
          style={{
            display: "flex",
            gap: 8,
            flexWrap: "wrap",
            marginBottom: 18,
            borderBottom: "1px solid #e5e7eb",
            paddingBottom: 6,
          }}
        >
          <button
            type="button"
            onClick={() => cambiarTab("TODAS")}
            style={{
              padding: "6px 14px",
              borderRadius: 999,
              border:
                tabActiva === "TODAS"
                  ? "2px solid #2563eb"
                  : "1px solid #d1d5db",
              background: tabActiva === "TODAS" ? "#eff6ff" : "#ffffff",
              color: tabActiva === "TODAS" ? "#1d4ed8" : "#374151",
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            Todas las asistencias
          </button>

          {clasesOrdenadas.map(c => (
            <button
              key={c.id_asist}
              type="button"
              onClick={() => cambiarTab(String(c.id_asist))}
              style={{
                padding: "6px 14px",
                borderRadius: 999,
                border:
                  String(tabActiva) === String(c.id_asist)
                    ? "2px solid #2563eb"
                    : "1px solid #d1d5db",
                background:
                  String(tabActiva) === String(c.id_asist)
                    ? "#eff6ff"
                    : "#ffffff",
                color:
                  String(tabActiva) === String(c.id_asist)
                    ? "#1d4ed8"
                    : "#374151",
                fontSize: ".9rem",
                cursor: "pointer",
              }}
            >
              {c.fecha_clase} • Aula {c.id_aula}
            </button>
          ))}
        </div>
      )}

      {tabActiva === "TODAS" && filasResumen.length > 0 && (
        <div className="table-responsive">
          <table className="aulas-table">
            <thead>
              <tr>
                <th>Estudiante</th>
                {clasesOrdenadas.map(c => (
                  <th key={c.id_asist} style={{ textAlign: "center" }}>
                    {c.fecha_clase}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filasResumen.map(est => (
                <tr key={est.id_estudiante}>
                  <td>
                    {est.nombres} {est.apellidos}
                  </td>
                  {est.asistencias.map((val, i) => (
                    <td key={i} style={{ textAlign: "center" }}>
                      <Circulo lleno={val === "S"} />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tabActiva !== "TODAS" && estudiantes.length > 0 && (
        <>
          <div style={{ textAlign: "right", marginBottom: 10 }}>
            <button
              className="aulas-btn"
              type="button"
              onClick={guardarTodas}
              disabled={loading}
              style={{ minWidth: 170 }}
            >
              {loading ? "Guardando..." : "Guardar asistencia"}
            </button>
          </div>

          <div className="table-responsive">
            <table className="aulas-table">
              <thead>
                <tr>
                  <th>Estudiante</th>
                  <th style={{ textAlign: "center" }}>¿Presente?</th>
                </tr>
              </thead>
              <tbody>
                {estudiantes.map(e => {
                  const marca = marcas[e.id_estudiante] || "N";
                  const esPresente = marca === "S";
                  return (
                    <tr key={e.id_estudiante}>
                      <td>
                        {e.nombres} {e.apellidos}
                      </td>
                      <td style={{ textAlign: "center" }}>
                        <button
                          type="button"
                          onClick={() => toggleAsistencia(e.id_estudiante)}
                          disabled={loading}
                          style={{
                            width: 26,
                            height: 26,
                            borderRadius: "999px",
                            border: esPresente
                              ? "2px solid #16a34a"
                              : "2px solid #9ca3af",
                            background: esPresente ? "#bbf7d0" : "#ffffff",
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            cursor: "pointer",
                          }}
                          title={esPresente ? "Presente" : "Ausente"}
                        >
                          {esPresente ? "●" : ""}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tabActiva !== "TODAS" && estudiantes.length === 0 && clases.length > 0 && (
        <div style={{ marginTop: 12, color: "#666" }}>
          No hay estudiantes registrados para la clase seleccionada.
        </div>
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

export default TomaDeAsistenciaEstudiante;
