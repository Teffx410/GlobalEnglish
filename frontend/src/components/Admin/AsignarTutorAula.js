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
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Cargar aulas
    axios.get("http://localhost:8000/aulas")
      .then(r => setAulas(r.data || []))
      .catch(err => {
        console.error("Error cargando aulas:", err);
        setError("No se pudieron cargar las aulas");
      });

    // Cargar personas y filtrar tutores
    axios.get("http://localhost:8000/personas")
      .then(r => {
        const tutores = (r.data || []).filter(p => p.rol === "TUTOR");
        setPersonas(tutores);
      })
      .catch(err => {
        console.error("Error cargando personas:", err);
        setError("No se pudieron cargar los tutores");
      });
  }, []);

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));

    if (name === "id_aula") {
      setHistorial([]);
      if (value) {
        axios.get(`http://localhost:8000/historial-tutores-aula/${value}`)
          .then(r => setHistorial(r.data || []))
          .catch(err => {
            console.error("Error cargando historial:", err);
            setHistorial([]);
          });
      }
    }
  }

  function asignarTutor(e) {
    e.preventDefault();
    console.log("CLICK asignar tutor", form);
    setMsg("");
    setError("");

    if (!form.id_aula || !form.id_persona || !form.fecha_inicio) {
      setError("Todos los campos requeridos deben estar llenos");
      return;
    }

    setLoading(true);

    const payload = {
      id_aula: parseInt(form.id_aula, 10),
      id_persona: parseInt(form.id_persona, 10),
      fecha_inicio: form.fecha_inicio,        // 'YYYY-MM-DD'
      motivo_cambio: form.motivo_cambio || null,
    };

    axios.post("http://localhost:8000/asignar-tutor-aula", payload)
      .then(r => {
        console.log("RESP asignar tutor:", r);
        setMsg(r.data.msg || "Tutor asignado correctamente.");
        if (form.id_aula) {
          axios.get(`http://localhost:8000/historial-tutores-aula/${form.id_aula}`)
            .then(r2 => setHistorial(r2.data || []));
        }
        setForm(f => ({
          ...f,
          id_persona: "",
          fecha_inicio: "",
          motivo_cambio: "",
        }));
      })
      .catch(err => {
        console.error("AXIOS ERROR asignar tutor:", err);
        if (err.response?.data?.detail) {
          setError(err.response.data.detail);
        } else if (err.response?.data?.error) {
          setError(err.response.data.error);
        } else if (err.message) {
          setError("Error al asignar tutor: " + err.message);
        } else {
          setError("Error al asignar tutor.");
        }
      })
      .finally(() => setLoading(false));
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
          disabled={loading}
        >
          <option value="">Selecciona un aula</option>
          {aulas.map(a => (
            <option key={a.id_aula} value={a.id_aula}>
              Aula #{a.id_aula} - {a.grado}° - Inst {a.id_institucion} (Sede {a.id_sede})
            </option>
          ))}
        </select>

        <select
          className="aulas-form-input"
          name="id_persona"
          value={form.id_persona}
          onChange={handleFormChange}
          required
          disabled={loading}
        >
          <option value="">Selecciona un tutor</option>
          {personas.map(p => (
            <option key={p.id_persona} value={p.id_persona}>
              {p.nombre} ({p.correo})
            </option>
          ))}
        </select>

        <input
          className="aulas-form-input"
          type="date"
          name="fecha_inicio"
          value={form.fecha_inicio}
          onChange={handleFormChange}
          required
          disabled={loading}
        />

        <input
          className="aulas-form-input"
          type="text"
          name="motivo_cambio"
          value={form.motivo_cambio}
          onChange={handleFormChange}
          placeholder="Motivo del cambio (opcional)"
          disabled={loading}
        />

        <button
          type="submit"
          className="aulas-btn"
          disabled={loading || !form.id_aula || !form.id_persona || !form.fecha_inicio}
        >
          {loading ? "Asignando..." : "Asignar Tutor"}
        </button>
      </form>

      {msg && (
        <div style={{
          color: "green",
          marginBottom: "10px",
          background: "#d4edda",
          borderRadius: "4px",
          padding: "8px"
        }}>
          {msg}
        </div>
      )}

      {error && (
        <div style={{
          color: "red",
          marginBottom: "10px",
          background: "#f8d7da",
          borderRadius: "4px",
          padding: "8px"
        }}>
          {error}
        </div>
      )}

      <h3>Historial de tutores del aula</h3>
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID</th>
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
                <td>{h.fecha_inicio || "-"}</td>
                <td>{h.fecha_fin || "[Activo]"}</td>
                <td>{h.motivo_cambio || "-"}</td>
              </tr>
            ))}
            {historial.length === 0 && (
              <tr>
                <td colSpan={6} style={{ textAlign: "center", color: "#666" }}>
                  Selecciona un aula para ver historial
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AsignarTutorAula;
