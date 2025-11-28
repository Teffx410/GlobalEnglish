// src/components/AsignarHorarioAula.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

const BASE = "http://localhost:8000";

function AsignarHorarioAula() {
  const [aulas, setAulas] = useState([]);
  const [horarios, setHorarios] = useState([]);
  const [form, setForm] = useState({
    id_aula: "",
    id_horario: "",
    fecha_inicio: ""
  });
  const [msg, setMsg] = useState("");
  const [historial, setHistorial] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get(`${BASE}/aulas`)
      .then(r => setAulas(r.data || []))
      .catch(err => {
        console.error("Error cargando aulas:", err);
        setMsg("Error al cargar aulas");
      });

    axios.get(`${BASE}/horarios`)
      .then(r => setHorarios(r.data || []))
      .catch(err => {
        console.error("Error cargando horarios:", err);
        setMsg("Error al cargar horarios");
      });
  }, []);

  function cargarHistorial(idAula) {
    if (!idAula) {
      setHistorial([]);
      return;
    }
    axios.get(`${BASE}/historial-horarios-aula/${idAula}`)
      .then(r => setHistorial(r.data || []))
      .catch(err => {
        console.error("Error cargando historial:", err);
        setHistorial([]);
      });
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
    if (name === "id_aula") {
      cargarHistorial(value);
    }
  }

  function asignarHorario(e) {
    e.preventDefault();
    setMsg("");
    setLoading(true);

    axios.post(`${BASE}/asignar-horario-aula`, form)
      .then(r => {
        setMsg(r.data.msg || "Horario asignado correctamente.");
        cargarHistorial(form.id_aula);
      })
      .catch(err => {
        console.error("Error asignar horario:", err);
        setMsg(err.response?.data?.detail || "Error al asignar horario.");
      })
      .finally(() => setLoading(false));
  }

  function finalizarHistorial(idHist) {
    if (!window.confirm("¿Marcar este horario como finalizado?")) return;
    setMsg("");
    axios.put(`${BASE}/historial-horarios-aula/${idHist}/fin`)
      .then(r => {
        setMsg(r.data.msg || "Horario marcado como finalizado.");
        cargarHistorial(form.id_aula);
      })
      .catch(err => {
        console.error("Error finalizar horario:", err);
        setMsg(err.response?.data?.detail || "Error al finalizar horario.");
      });
  }

  return (
    <div className="instituciones-panel">
      <h2>Asignar Horario a Aula</h2>

      <form className="instituciones-form" onSubmit={asignarHorario}>
        <select
          className="aulas-form-input"
          name="id_aula"
          value={form.id_aula}
          onChange={handleFormChange}
          required
          disabled={loading}
        >
          <option value="">Aula</option>
          {aulas.map(a => (
            <option key={a.id_aula} value={a.id_aula}>
              Aula #{a.id_aula} - Grado {a.grado} - Inst {a.id_institucion} Sede {a.id_sede}
            </option>
          ))}
        </select>

        <select
          className="aulas-form-input"
          name="id_horario"
          value={form.id_horario}
          onChange={handleFormChange}
          required
          disabled={loading}
        >
          <option value="">Horario</option>
          {horarios.map(h => (
            <option key={h.id_horario} value={h.id_horario}>
              {h.dia_semana} {h.h_inicio}-{h.h_final} ({h.minutos_equiv} min {h.es_continuo === "S" ? "Cont." : "No"})
            </option>
          ))}
        </select>

        <input
          className="aulas-form-input"
          type="date"
          name="fecha_inicio"
          value={form.fecha_inicio}
          onChange={handleFormChange}
          disabled={loading}
        />

        <button
          type="submit"
          className="aulas-btn"
          disabled={loading || !form.id_aula || !form.id_horario}
        >
          {loading ? "Asignando..." : "Asignar Horario"}
        </button>
      </form>

      {msg && (
        <div style={{ marginBottom: "10px" }}>
          {msg}
        </div>
      )}

      <h3>Historial horarios aula</h3>
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID hist</th>
              <th>ID Horario</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Día</th>
              <th>Horario</th>
              <th>Min.</th>
              <th>Cont.</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {historial.map(h => (
              <tr key={h.id_hist_horario}>
                <td>{h.id_hist_horario}</td>
                <td>{h.id_horario}</td>
                <td>{h.fecha_inicio}</td>
                <td>{h.fecha_fin || "[Activo]"}</td>
                <td>{h.dia_semana}</td>
                <td>{h.h_inicio} - {h.h_final}</td>
                <td>{h.minutos_equiv}</td>
                <td>{h.es_continuo === "S" ? "Sí" : "No"}</td>
                <td>
                  {!h.fecha_fin && (
                    <button
                      type="button"
                      className="btn-editar"
                      onClick={() => finalizarHistorial(h.id_hist_horario)}
                    >
                      Finalizar
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {historial.length === 0 && (
              <tr>
                <td colSpan={9}>No hay historial</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AsignarHorarioAula;
