import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function Horarios() {
  const [horarios, setHorarios] = useState([]);
  const [form, setForm] = useState({
    dia_semana: "",
    h_inicio: "",
    h_final: "",
    minutos_equiv: 60,
<<<<<<< HEAD
    es_continuo: "S"
=======
    es_continuo: "S",
>>>>>>> main
  });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    cargarHorarios();
  }, []);

  function cargarHorarios() {
<<<<<<< HEAD
    axios.get("http://localhost:8000/horarios").then(r => setHorarios(r.data));
=======
    axios
      .get("http://localhost:8000/horarios")
      .then((r) => setHorarios(r.data))
      .catch(() => setMsg("Error al cargar horarios"));
>>>>>>> main
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
<<<<<<< HEAD
    setForm(f => ({ ...f, [name]: value }));
=======
    setForm((f) => ({ ...f, [name]: value }));
>>>>>>> main
  }

  function agregarHorario(e) {
    e.preventDefault();
<<<<<<< HEAD
    // Puedes ajustar el grado/jornada según el contexto de asignación real
    axios.post("http://localhost:8000/horarios?grado=4&jornada_institucion=MAÑANA", form)
      .then(r => {
        setMsg("Horario registrado (ID: " + r.data.id_horario + ")");
        cargarHorarios();
        setForm({ dia_semana: "", h_inicio: "", h_final: "", minutos_equiv: 60, es_continuo: "S" });
      })
      .catch(err => setMsg(err.response?.data?.detail || "Error al registrar horario"));
=======

    axios
      .post("http://localhost:8000/horarios", form)
      .then((r) => {
        setMsg("Horario registrado (ID: " + r.data.id_horario + ")");
        cargarHorarios();
        setForm({
          dia_semana: "",
          h_inicio: "",
          h_final: "",
          minutos_equiv: 60,
          es_continuo: "S",
        });
      })
      .catch((err) =>
        setMsg(err.response?.data?.detail || "Error al registrar horario")
      );
>>>>>>> main
  }

  function eliminarHorario(id) {
    if (!window.confirm("¿Eliminar este horario?")) return;
<<<<<<< HEAD
    axios.delete(`http://localhost:8000/horarios/${id}`).then(() => {
      setMsg("Horario eliminado");
      cargarHorarios();
    });
=======
    axios
      .delete(`http://localhost:8000/horarios/${id}`)
      .then(() => {
        setMsg("Horario eliminado");
        cargarHorarios();
      })
      .catch(() => setMsg("Error al eliminar horario"));
>>>>>>> main
  }

  return (
    <div className="instituciones-panel">
      <h2>Registrar Horario</h2>
      <form className="instituciones-form" onSubmit={agregarHorario}>
<<<<<<< HEAD
        <select className="aulas-form-input" name="dia_semana" value={form.dia_semana} onChange={handleFormChange} required>
          <option value="">Día</option>
          <option value="Lunes">Lunes</option>
          <option value="Martes">Martes</option>
          <option value="Miércoles">Miércoles</option>
          <option value="Jueves">Jueves</option>
          <option value="Viernes">Viernes</option>
          <option value="Sábado">Sábado</option>
          <option value="Domingo">Domingo</option>
        </select>
        <input className="aulas-form-input" type="time" name="h_inicio" value={form.h_inicio} onChange={handleFormChange} required/>
        <input className="aulas-form-input" type="time" name="h_final" value={form.h_final} onChange={handleFormChange} required/>
        <select className="aulas-form-input" name="minutos_equiv" value={form.minutos_equiv} onChange={handleFormChange} required>
          <option value={60}>60 minutos</option>
          <option value={40}>40 minutos</option>
          <option value={45}>45 minutos</option>
          <option value={50}>50 minutos</option>
          <option value={55}>55 minutos</option>
        </select>
        <select className="aulas-form-input" name="es_continuo" value={form.es_continuo} onChange={handleFormChange}>
          <option value="S">Continuo</option>
          <option value="N">No Continuo</option>
        </select>
        <button type="submit" className="aulas-btn">Registrar Horario</button>
      </form>
      {msg && <div style={{ color: "green", marginBottom: "10px" }}>{msg}</div>}
=======
        {/* Día de la semana */}
        <label className="aulas-form-label">
          Día de la semana
          <select
            className="aulas-form-input"
            name="dia_semana"
            value={form.dia_semana}
            onChange={handleFormChange}
            required
          >
            <option value="">Selecciona un día</option>
            <option value="Lunes">Lunes</option>
            <option value="Martes">Martes</option>
            <option value="Miércoles">Miércoles</option>
            <option value="Jueves">Jueves</option>
            <option value="Viernes">Viernes</option>
            <option value="Sábado">Sábado</option>
            <option value="Domingo">Domingo</option>
          </select>
        </label>

        {/* Hora inicio */}
        <label className="aulas-form-label">
          Hora de inicio
          <input
            className="aulas-form-input"
            type="time"
            name="h_inicio"
            value={form.h_inicio}
            onChange={handleFormChange}
            required
          />
        </label>

        {/* Hora fin */}
        <label className="aulas-form-label">
          Hora de fin
          <input
            className="aulas-form-input"
            type="time"
            name="h_final"
            value={form.h_final}
            onChange={handleFormChange}
            required
          />
        </label>

        {/* Minutos equivalentes */}
        <label className="aulas-form-label">
          Minutos equivalentes
          <select
            className="aulas-form-input"
            name="minutos_equiv"
            value={form.minutos_equiv}
            onChange={handleFormChange}
            required
          >
            <option value={60}>60 minutos</option>
            <option value={40}>40 minutos</option>
            <option value={45}>45 minutos</option>
            <option value={50}>50 minutos</option>
            <option value={55}>55 minutos</option>
          </select>
        </label>

        {/* Continuo / No continuo */}
        <label className="aulas-form-label">
          ¿Es continuo?
          <select
            className="aulas-form-input"
            name="es_continuo"
            value={form.es_continuo}
            onChange={handleFormChange}
          >
            <option value="S">Continuo</option>
            <option value="N">No Continuo</option>
          </select>
        </label>

        <button type="submit" className="aulas-btn">
          Registrar Horario
        </button>
      </form>

      {msg && (
        <div style={{ color: "green", marginBottom: "10px" }}>{msg}</div>
      )}

>>>>>>> main
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Día</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Equiv. Min</th>
              <th>Continuo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
<<<<<<< HEAD
            {horarios.map(h => (
=======
            {horarios.map((h) => (
>>>>>>> main
              <tr key={h.id_horario}>
                <td>{h.id_horario}</td>
                <td>{h.dia_semana}</td>
                <td>{h.h_inicio}</td>
                <td>{h.h_final}</td>
                <td>{h.minutos_equiv}</td>
                <td>{h.es_continuo === "S" ? "Sí" : "No"}</td>
                <td>
<<<<<<< HEAD
                  <button className="btn-eliminar" onClick={() => eliminarHorario(h.id_horario)}>Eliminar</button>
                </td>
              </tr>
            ))}
            {horarios.length === 0 &&
              <tr><td colSpan={7}>No hay horarios registrados</td></tr>}
=======
                  <button
                    className="btn-eliminar"
                    onClick={() => eliminarHorario(h.id_horario)}
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
            {horarios.length === 0 && (
              <tr>
                <td colSpan={7}>No hay horarios registrados</td>
              </tr>
            )}
>>>>>>> main
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Horarios;
