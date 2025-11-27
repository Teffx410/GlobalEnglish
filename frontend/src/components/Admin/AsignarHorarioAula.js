import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function AsignarHorarioAula() {
  const [aulas, setAulas] = useState([]);
  const [horarios, setHorarios] = useState([]);
  const [form, setForm] = useState({
    id_aula: "",
    id_horario: "",
<<<<<<< HEAD
    fecha_inicio: "",
  });
  const [msg, setMsg] = useState("");
  const [historial, setHistorial] = useState([]);
  const BASE = "http://localhost:8000";

  useEffect(() => {
    axios.get(`${BASE}/aulas`).then(r => setAulas(r.data));
    axios.get(`${BASE}/horarios`).then(r => setHorarios(r.data));
=======
    fecha_inicio: ""
  });
  const [msg, setMsg] = useState("");
  const [historial, setHistorial] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/aulas").then(r => setAulas(r.data));
    axios.get("http://localhost:8000/horarios").then(r => setHorarios(r.data));
>>>>>>> main
  }, []);

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
    if (name === "id_aula" && value) {
<<<<<<< HEAD
      axios.get(`${BASE}/historial-horarios-aula/${value}`)
        .then(r => setHistorial(r.data));
    }
  }

  function asignarHorario(e) {
    e.preventDefault();
    setMsg("");
    axios.post(`${BASE}/asignar-horario-aula`, form)
      .then(r => {
        setMsg(r.data.msg || "Horario asignado correctamente.");
        if (form.id_aula) {
          axios.get(`${BASE}/historial-horarios-aula/${form.id_aula}`)
            .then(r => setHistorial(r.data));
        }
      })
      .catch(err => {
        if (err.response && err.response.data && err.response.data.detail) {
          setMsg(err.response.data.detail); // Muestra mensajes del backend
        } else {
          setMsg("Error al asignar horario.");
        }
        if (form.id_aula) {
          axios.get(`${BASE}/historial-horarios-aula/${form.id_aula}`)
            .then(r => setHistorial(r.data));
        }
      });
=======
      axios.get(`http://localhost:8000/historial-horarios-aula/${value}`)
        .then(r => setHistorial(r.data));
    }
  }
  function finalizarHistorial(idHist) {
  if (!window.confirm("¿Marcar este horario como finalizado?")) return;
  axios
    .put(`http://localhost:8000/historial-horarios-aula/${idHist}/fin`)
    .then(() => {
      setMsg("Horario marcado como finalizado");
      if (form.id_aula) {
        axios
          .get(`http://localhost:8000/historial-horarios-aula/${form.id_aula}`)
          .then((r) => setHistorial(r.data));
      }
    })
    .catch((err) => {
      setMsg(err.response?.data?.detail || "Error al finalizar horario");
    });
}
  function asignarHorario(e) {
    e.preventDefault();
    axios.post("http://localhost:8000/asignar-horario-aula", form)
      .then(r => {
        setMsg(r.data.msg);
        if (form.id_aula) {
          axios.get(`http://localhost:8000/historial-horarios-aula/${form.id_aula}`)
            .then(r => setHistorial(r.data));
        }
      })
      .catch(() => setMsg("Error al asignar horario"));
>>>>>>> main
  }

  return (
    <div className="instituciones-panel">
      <h2>Asignar Horario a Aula</h2>
      <form className="instituciones-form" onSubmit={asignarHorario}>
<<<<<<< HEAD
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
              Aula #{a.id_aula} - Grado {a.grado}
            </option>
          )}
        </select>
        <select
          className="aulas-form-input"
          name="id_horario"
          value={form.id_horario}
          onChange={handleFormChange}
          required
        >
          <option value="">Horario</option>
          {horarios.map(h =>
            <option key={h.id_horario} value={h.id_horario}>
              {h.dia_semana} {h.h_inicio}-{h.h_final}
            </option>
          )}
        </select>
        <input
          className="aulas-form-input"
          type="date"
          name="fecha_inicio"
          value={form.fecha_inicio}
          onChange={handleFormChange}
        />
        <button type="submit" className="aulas-btn">Asignar Horario</button>
      </form>
      {msg && (
        <div style={{
          color: msg.includes("Error") || msg.toLowerCase().includes("cruce") || msg.toLowerCase().includes("excede") ? "red" : "green",
          marginBottom: "10px"
        }}>
          {msg}
        </div>
      )}
=======
        <select className="aulas-form-input" name="id_aula" value={form.id_aula} onChange={handleFormChange} required>
          <option value="">Aula</option>
          {aulas.map(a =>
            <option key={a.id_aula} value={a.id_aula}>
              Aula #{a.id_aula} - Grado {a.grado} - Inst {a.id_institucion} Sede {a.id_sede}
            </option>
          )}
        </select>
        <select className="aulas-form-input" name="id_horario" value={form.id_horario} onChange={handleFormChange} required>
          <option value="">Horario</option>
          {horarios.map(h =>
            <option key={h.id_horario} value={h.id_horario}>
              {h.dia_semana} {h.h_inicio}-{h.h_final} ({h.minutos_equiv} min {h.es_continuo === "S" ? "Cont." : "No"})
            </option>
          )}
        </select>
        <input className="aulas-form-input" type="date" name="fecha_inicio" value={form.fecha_inicio} onChange={handleFormChange}/>
        <button type="submit" className="aulas-btn">Asignar Horario</button>
      </form>
      {msg && <div style={{ color: "green", marginBottom: "10px" }}>{msg}</div>}
>>>>>>> main
      <h3>Historial horarios aula</h3>
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID hist</th>
<<<<<<< HEAD
              <th>ID Horario</th>
=======
              <th>Horario</th>
>>>>>>> main
              <th>Inicio</th>
              <th>Fin</th>
              <th>Día</th>
              <th>Horario</th>
              <th>Min.</th>
              <th>Cont.</th>
<<<<<<< HEAD
            </tr>
          </thead>
          <tbody>
            {historial.map(h => (
=======
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {historial.map((h) => (
>>>>>>> main
              <tr key={h.id_hist_horario}>
                <td>{h.id_hist_horario}</td>
                <td>{h.id_horario}</td>
                <td>{h.fecha_inicio}</td>
                <td>{h.fecha_fin || "[Activo]"}</td>
                <td>{h.dia_semana}</td>
                <td>{h.h_inicio} - {h.h_final}</td>
                <td>{h.minutos_equiv}</td>
                <td>{h.es_continuo === "S" ? "Sí" : "No"}</td>
<<<<<<< HEAD
              </tr>
            ))}
            {historial.length === 0 &&
              <tr><td colSpan={8}>No hay historial</td></tr>}
=======
                <td>
                  {!h.fecha_fin && (
                    <button
                      className="btn-editar"
                      type="button"
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
>>>>>>> main
          </tbody>
        </table>
      </div>
    </div>
  );
}
<<<<<<< HEAD

=======
>>>>>>> main
export default AsignarHorarioAula;
