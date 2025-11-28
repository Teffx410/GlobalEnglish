<<<<<<< HEAD
// src/components/AsignarTutorAula.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function AsignarTutorAula() {
  const [aulas, setAulas] = useState([]);
  const [personas, setPersonas] = useState([]);
  const [form, setForm] = useState({
    id_aula: "",
    id_persona: "",
    fecha_inicio: "",
    motivo_cambio: "",
  });
  const [msg, setMsg] = useState("");
  const [historial, setHistorial] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    axios.get("http://localhost:8000/aulas").then(r => setAulas(r.data));
    axios.get("http://localhost:8000/personas").then(r => {
      setPersonas(r.data.filter(p => p.rol === "TUTOR"));
    });
  }, []);

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
    if (name === "id_aula" && value) {
      axios.get(`http://localhost:8000/historial-tutores-aula/${value}`)
        .then(r => setHistorial(r.data));
    }
  }

  function asignarTutor(e) {
    e.preventDefault();
    setMsg("");
    setError("");
    axios.post("http://localhost:8000/asignar-tutor-aula", form)
      .then(r => {
        setMsg(r.data.msg || "Tutor asignado correctamente.");
        if (form.id_aula) {
          axios.get(`http://localhost:8000/historial-tutores-aula/${form.id_aula}`)
            .then(r => setHistorial(r.data));
        }
      })
      .catch(err => {
        if (err.response && err.response.data && err.response.data.detail) {
          setError(err.response.data.detail);
        } else {
          setError("Error al asignar tutor.");
        }
        // Refresca historial aunque haya error
        if (form.id_aula) {
          axios.get(`http://localhost:8000/historial-tutores-aula/${form.id_aula}`)
            .then(r => setHistorial(r.data));
        }
      });
  }

  return (
    <div className="instituciones-panel">
      <h2>Asignar Tutor a Aula</h2>
      <form className="instituciones-form" onSubmit={asignarTutor}>
        <select
          className="aulas-form-input"
          name="id_aula"
          value={form.id_aula}
          onChange={handleFormChange}
          required
        >
          <option value="">Aula</option>
          {aulas.map(a =>
            <option key={a.id_aula} value={a.id_aula}>
              Aula #{a.id_aula} - Grado {a.grado} - Inst {a.id_institucion} Sede {a.id_sede}
            </option>
          )}
        </select>
        <select
          className="aulas-form-input"
          name="id_persona"
          value={form.id_persona}
          onChange={handleFormChange}
          required
        >
          <option value="">Tutor</option>
          {personas.map(p =>
            <option key={p.id_persona} value={p.id_persona}>
              {p.nombre} ({p.correo})
            </option>
          )}
        </select>
        <input
          className="aulas-form-input"
          type="date"
          name="fecha_inicio"
          value={form.fecha_inicio}
          onChange={handleFormChange}
          required
        />
        <input
          className="aulas-form-input"
          type="text"
          name="motivo_cambio"
          value={form.motivo_cambio}
          onChange={handleFormChange}
          placeholder="Motivo (opcional)"
        />
        <button type="submit" className="aulas-btn">
          Asignar Tutor
        </button>
      </form>
      {msg && (
        <div style={{ color: "green", marginBottom: "10px" }}>{msg}</div>
      )}
      {error && (
        <div style={{
          color: "red",
          marginBottom: "10px",
          background: "#ffdede",
          borderRadius: "4px",
          padding: "8px"
        }}>{error}</div>
      )}
      <h3>Historial tutores aula</h3>
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID hist</th>
              <th>Tutor</th>
              <th>Correo</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Motivo</th>
            </tr>
          </thead>
          <tbody>
            {historial.map(h => (
              <tr key={h.id_tutor_aula}>
                <td>{h.id_tutor_aula}</td>
                <td>{h.nombre_tutor}</td>
                <td>{h.correo_tutor}</td>
                <td>{h.fecha_inicio}</td>
                <td>{h.fecha_fin || "[Activo]"}</td>
                <td>{h.motivo_cambio || "-"}</td>
              </tr>
            ))}
            {historial.length === 0 &&
              <tr><td colSpan={6}>No hay historial</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
export default AsignarTutorAula;
