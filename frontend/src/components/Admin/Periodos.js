import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function Periodos() {
  const [periodos, setPeriodos] = useState([]);
  const [form, setForm] = useState({ nombre: "", fecha_inicio: "", fecha_fin: "" });
  const [msg, setMsg] = useState("");

  useEffect(() => { cargarPeriodos(); }, []);
  function cargarPeriodos() { axios.get("http://localhost:8000/periodos").then(r => setPeriodos(r.data)); }
  function handleFormChange(e) { const { name, value } = e.target; setForm(f => ({ ...f, [name]: value })); }
  function agregarPeriodo(e) {
    e.preventDefault();
    axios.post("http://localhost:8000/periodos", form).then(r => {
      setMsg(r.data.msg);
      cargarPeriodos();
      setForm({ nombre: "", fecha_inicio: "", fecha_fin: "" });
    }).catch(() => setMsg("Error al crear periodo"));
  }

  return (
    <div className="instituciones-panel">
      <h2>Registrar Periodo</h2>
      <form className="instituciones-form" onSubmit={agregarPeriodo}>
        <input className="aulas-form-input" name="nombre" value={form.nombre} onChange={handleFormChange} placeholder="Nombre del periodo" required />
        <input className="aulas-form-input" type="date" name="fecha_inicio" value={form.fecha_inicio} onChange={handleFormChange} required />
        <input className="aulas-form-input" type="date" name="fecha_fin" value={form.fecha_fin} onChange={handleFormChange} required />
        <button type="submit" className="aulas-btn">Registrar Periodo</button>
      </form>
      {msg && <div style={{ color: "green", marginBottom: "10px" }}>{msg}</div>}
      <div className="table-responsive">
        <table className="aulas-table">
          <thead><tr><th>ID</th><th>Nombre</th><th>Inicio</th><th>Fin</th></tr></thead>
          <tbody>
            {periodos.map(p => (
              <tr key={p.id_periodo}>
                <td>{p.id_periodo}</td>
                <td>{p.nombre}</td>
                <td>{p.fecha_inicio}</td>
                <td>{p.fecha_fin}</td>
              </tr>
            ))}
            {periodos.length === 0 && <tr><td colSpan={4}>No hay periodos registrados</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
export default Periodos;
