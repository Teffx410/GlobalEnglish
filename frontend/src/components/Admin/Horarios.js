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
    es_continuo: "S"
  });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    cargarHorarios();
  }, []);

  function cargarHorarios() {
    axios.get("http://localhost:8000/horarios").then(r => setHorarios(r.data));
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  }

  function agregarHorario(e) {
    e.preventDefault();
    // Puedes ajustar el grado/jornada según el contexto de asignación real
    axios.post("http://localhost:8000/horarios?grado=4&jornada_institucion=MAÑANA", form)
      .then(r => {
        setMsg("Horario registrado (ID: " + r.data.id_horario + ")");
        cargarHorarios();
        setForm({ dia_semana: "", h_inicio: "", h_final: "", minutos_equiv: 60, es_continuo: "S" });
      })
      .catch(err => setMsg(err.response?.data?.detail || "Error al registrar horario"));
  }

  function eliminarHorario(id) {
    if (!window.confirm("¿Eliminar este horario?")) return;
    axios.delete(`http://localhost:8000/horarios/${id}`).then(() => {
      setMsg("Horario eliminado");
      cargarHorarios();
    });
  }

  return (
    <div className="instituciones-panel">
      <h2>Registrar Horario</h2>
      <form className="instituciones-form" onSubmit={agregarHorario}>
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
            {horarios.map(h => (
              <tr key={h.id_horario}>
                <td>{h.id_horario}</td>
                <td>{h.dia_semana}</td>
                <td>{h.h_inicio}</td>
                <td>{h.h_final}</td>
                <td>{h.minutos_equiv}</td>
                <td>{h.es_continuo === "S" ? "Sí" : "No"}</td>
                <td>
                  <button className="btn-eliminar" onClick={() => eliminarHorario(h.id_horario)}>Eliminar</button>
                </td>
              </tr>
            ))}
            {horarios.length === 0 &&
              <tr><td colSpan={7}>No hay horarios registrados</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Horarios;
