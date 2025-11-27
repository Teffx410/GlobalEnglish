import React, { useState, useEffect } from "react";
import axios from "axios";

const BASE = "http://localhost:8000";

function AdminIngresoNotas() {
  const [tutores, setTutores] = useState([]);
  const [aulas, setAulas] = useState([]);
  const [estudiantes, setEstudiantes] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [componentes, setComponentes] = useState([]);

  const [tutorSel, setTutorSel] = useState("");
  const [aulaSel, setAulaSel] = useState("");
  const [periodoSel, setPeriodoSel] = useState("");
  const [componenteSel, setComponenteSel] = useState("");
  const [notas, setNotas] = useState({});
  const [msg, setMsg] = useState("");
  const [cargando, setCargando] = useState(false);

  // Cargar tutores y períodos al montar
  useEffect(() => {
    axios.get(`${BASE}/admin/listar-tutores`).then(res => setTutores(res.data));
    axios.get(`${BASE}/admin/listar-periodos`).then(res => setPeriodos(res.data));
  }, []);

  // Cambiar tutor
  const handleTutorChange = async val => {
    setTutorSel(val);
    setAulaSel("");
    setEstudiantes([]);
    setNotas({});
    if (!val) {
      setAulas([]);
      return;
    }
    let res = await axios.get(`${BASE}/admin/listar-aulas-tutor?id_persona=${val}`);
    setAulas(res.data);
  };

  // Cambiar aula
  const handleAulaChange = async val => {
    setAulaSel(val);
    setEstudiantes([]);
    setNotas({});
    if (!val) return;
    let res = await axios.get(`${BASE}/admin/listar-estudiantes-aula?id_aula=${val}`);
    setEstudiantes(res.data);
  };

  // Cambiar período
  const handlePeriodoChange = async val => {
    setPeriodoSel(val);
    setComponenteSel("");
    setNotas({});
    if (!val) {
      setComponentes([]);
      return;
    }
    let res = await axios.get(`${BASE}/admin/listar-componentes-periodo?id_periodo=${val}`);
    setComponentes(res.data);
  };

  // Función para cargar notas desde el backend
  const cargarNotas = async (id_componente, id_periodo) => {
    setCargando(true);
    const notasDict = {};
    try {
      for (const est of estudiantes) {
        let res = await axios.get(
          `${BASE}/admin/obtener-nota-estudiante?id_estudiante=${est.id_estudiante}&id_periodo=${id_periodo}&id_componente=${id_componente}`
        );
        notasDict[est.id_estudiante] = res.data.nota !== null && res.data.nota !== undefined ? res.data.nota : "";
      }
      setNotas(notasDict);
    } catch (e) {
      console.error("Error cargando notas:", e);
    }
    setCargando(false);
  };

  // Cambiar componente (cargar notas existentes)
  const handleComponenteChange = async val => {
    setComponenteSel(val);
    if (!val) {
      setNotas({});
      return;
    }
    await cargarNotas(val, periodoSel);
  };

  // Cambiar nota de un estudiante (SOLO en memoria local, temporal)
  const handleNotaChange = (id_est, valor) => {
    setNotas(prev => ({ ...prev, [id_est]: valor }));
  };

  // Guardar nota
  const handleGuardarNota = async (id_est) => {
    setMsg("");
    const notaIngresada = notas[id_est];
    const nota = parseFloat(notaIngresada);
    
    if (isNaN(nota) || notaIngresada === "" || notaIngresada === undefined) {
      setMsg("Ingresa un número válido");
      return;
    }
    
    if (nota < 0 || nota > 5) {
      setMsg("La nota debe estar entre 0 y 5");
      return;
    }

    try {
      let res = await axios.post(`${BASE}/admin/registrar-nota-estudiante`, {
        id_estudiante: id_est,
        id_periodo: periodoSel,
        id_componente: componenteSel,
        nota: nota
      });
      
      setMsg(res.data.msg || "Nota guardada correctamente");
      
      // IMPORTANTE: Recargar SOLO esta nota desde la BD
      // Esto asegura que el frontend siempre tenga el valor de la BD
      let resNota = await axios.get(
        `${BASE}/admin/obtener-nota-estudiante?id_estudiante=${id_est}&id_periodo=${periodoSel}&id_componente=${componenteSel}`
      );
      
      setNotas(prev => ({ 
        ...prev, 
        [id_est]: resNota.data.nota !== null && resNota.data.nota !== undefined ? resNota.data.nota : "" 
      }));
      
      setTimeout(() => {
        setMsg("");
      }, 2000);
      
    } catch (e) {
      console.error("Error:", e);
      setMsg("Error al guardar nota: " + (e.response?.data?.msg || e.message));
    }
  };

  return (
    <div style={{ maxWidth: 1000, margin: "auto", padding: 20, background: "#fafdff", borderRadius: 8 }}>
      <h2 style={{ margin: "0 0 20px" }}>Ingreso de notas</h2>

      {/* Selección de tutor */}
      <div style={{ marginBottom: 16 }}>
        <label style={{ fontWeight: "bold", display: "inline-block", minWidth: 100 }}>Tutor:</label>
        <select 
          value={tutorSel} 
          onChange={e => handleTutorChange(e.target.value)} 
          style={{ 
            marginLeft: 10, 
            padding: "8px 12px", 
            borderRadius: 4, 
            border: "1px solid #aaa",
            minWidth: 250
          }}
        >
          <option value="">Seleccione tutor</option>
          {tutores.map(t => (
            <option value={t.id_persona} key={t.id_persona}>{t.nombre}</option>
          ))}
        </select>
      </div>

      {/* Selección de aula */}
      {aulas.length > 0 &&
        <div style={{ marginBottom: 16 }}>
          <label style={{ fontWeight: "bold", display: "inline-block", minWidth: 100 }}>Aula:</label>
          <select 
            value={aulaSel} 
            onChange={e => handleAulaChange(e.target.value)} 
            style={{ 
              marginLeft: 10, 
              padding: "8px 12px", 
              borderRadius: 4, 
              border: "1px solid #aaa",
              minWidth: 250
            }}
          >
            <option value="">Seleccione aula</option>
            {aulas.map(a => (
              <option value={a.id_aula} key={a.id_aula}>Grado {a.grado}</option>
            ))}
          </select>
        </div>
      }

      {/* Selección de período */}
      {estudiantes.length > 0 &&
        <div style={{ marginBottom: 16 }}>
          <label style={{ fontWeight: "bold", display: "inline-block", minWidth: 100 }}>Período:</label>
          <select 
            value={periodoSel} 
            onChange={e => handlePeriodoChange(e.target.value)} 
            style={{ 
              marginLeft: 10, 
              padding: "8px 12px", 
              borderRadius: 4, 
              border: "1px solid #aaa",
              minWidth: 250
            }}
          >
            <option value="">Seleccione período</option>
            {periodos.map(p => (
              <option value={p.id_periodo} key={p.id_periodo}>{p.nombre}</option>
            ))}
          </select>
        </div>
      }

      {/* Selección de componente */}
      {componentes.length > 0 &&
        <div style={{ marginBottom: 16 }}>
          <label style={{ fontWeight: "bold", display: "inline-block", minWidth: 100 }}>Componente:</label>
          <select 
            value={componenteSel} 
            onChange={e => handleComponenteChange(e.target.value)} 
            style={{ 
              marginLeft: 10, 
              padding: "8px 12px", 
              borderRadius: 4, 
              border: "1px solid #aaa",
              minWidth: 250
            }}
          >
            <option value="">Seleccione componente</option>
            {componentes.map(c => (
              <option value={c.id_componente} key={c.id_componente}>
                {c.nombre} ({c.porcentaje}%)
              </option>
            ))}
          </select>
        </div>
      }

      {/* Mensaje */}
      {msg && 
        <div style={{ 
          marginBottom: 16, 
          padding: 12, 
          background: msg.includes("Error") ? "#ffefef" : "#eaffea", 
          borderRadius: 4, 
          color: msg.includes("Error") ? "#a11" : "#237327",
          border: msg.includes("Error") ? "1px solid #fcc" : "1px solid #afd",
          fontWeight: "500"
        }}>
          {msg}
        </div>
      }

      {/* Tabla de notas */}
      {componenteSel && estudiantes.length > 0 &&
        <div style={{ marginTop: 20 }}>
          <h4 style={{ marginBottom: 12 }}>Ingresar notas</h4>
          {cargando && <div style={{ color: "#666", textAlign: "center", padding: "20px" }}>⏳ Cargando notas...</div>}
          {!cargando &&
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: "#eee" }}>
                    <th style={{ 
                      padding: 12, 
                      textAlign: "left", 
                      borderBottom: "2px solid #aaa",
                      fontWeight: "bold"
                    }}>Estudiante</th>
                    <th style={{ 
                      padding: 12, 
                      textAlign: "center", 
                      borderBottom: "2px solid #aaa",
                      fontWeight: "bold"
                    }}>Nota (0-5)</th>
                    <th style={{ 
                      padding: 12, 
                      textAlign: "center", 
                      borderBottom: "2px solid #aaa",
                      fontWeight: "bold"
                    }}>Guardar</th>
                  </tr>
                </thead>
                <tbody>
                  {estudiantes.map((e, idx) => (
                    <tr 
                      key={e.id_estudiante} 
                      style={{ 
                        borderBottom: "1px solid #ddd", 
                        background: idx % 2 === 0 ? "#f9f9f9" : "#fff"
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
                          value={notas[e.id_estudiante] ?? ""}
                          onChange={evt => handleNotaChange(e.id_estudiante, evt.target.value)}
                          style={{ 
                            width: 80, 
                            padding: "6px 8px",
                            border: "1px solid #ccc",
                            borderRadius: 4,
                            textAlign: "center"
                          }}
                          placeholder="0.0"
                        />
                      </td>
                      <td style={{ padding: 12, textAlign: "center" }}>
                        <button 
                          onClick={() => handleGuardarNota(e.id_estudiante)}
                          style={{
                            padding: "6px 14px",
                            background: "#1675ac",
                            color: "#fff",
                            border: "none",
                            borderRadius: 4,
                            cursor: "pointer",
                            fontSize: "0.9em",
                            fontWeight: "bold"
                          }}
                          onMouseOver={evt => evt.target.style.background = "#0f5a8f"}
                          onMouseOut={evt => evt.target.style.background = "#1675ac"}
                        >
                          Guardar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          }
        </div>
      }

      {/* Mensaje cuando no hay estudiantes */}
      {componenteSel && estudiantes.length === 0 && 
        <div style={{ marginTop: 20, color: "#999", fontStyle: "italic" }}>
          No hay estudiantes registrados para esta aula.
        </div>
      }
    </div>
  );
}

export default AdminIngresoNotas;
