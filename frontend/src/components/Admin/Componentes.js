import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function Componentes() {
  const [componentes, setComponentes] = useState([]);
  const [form, setForm] = useState({ nombre: "", porcentaje: "", tipo_programa: "" });
  const [msg, setMsg] = useState("");

  useEffect(() => { cargarComponentes(); }, []);
  function cargarComponentes() { axios.get("http://localhost:8000/componentes").then(r => setComponentes(r.data)); }
  function handleFormChange(e) { const { name, value } = e.target; setForm(f => ({ ...f, [name]: value })); }
  function agregarComponente(e) {
    e.preventDefault();
    axios.post("http://localhost:8000/componentes", form).then(r => {
      setMsg(r.data.msg);
      cargarComponentes();
      setForm({ nombre: "", porcentaje: "", tipo_programa: "" });
    }).catch(() => setMsg("Error al crear componente"));
  }

  return (
    <div className="instituciones-panel">
      <h2>Registrar Componente de Nota</h2>
      <form className="instituciones-form" onSubmit={agregarComponente}>
        <input className="aulas-form-input" name="nombre" value={form.nombre} onChange={handleFormChange} placeholder="Nombre componente" required />
        <input className="aulas-form-input" type="number" name="porcentaje" value={form.porcentaje} min="0" max="100" step="0.1" onChange={handleFormChange} placeholder="Porcentaje" required />
        <input className="aulas-form-input" name="tipo_programa" value={form.tipo_programa} onChange={handleFormChange} placeholder="Tipo de programa (opcional)" />
        <button type="submit" className="aulas-btn">Registrar Componente</button>
      </form>
      {msg && <div style={{ color: "green", marginBottom: "10px" }}>{msg}</div>}
      <div className="table-responsive">
        <table className="aulas-table">
          <thead><tr><th>ID</th><th>Nombre</th><th>%</th></tr></thead>
          <tbody>
            {componentes.map(c => (
              <tr key={c.id_componente}>
                <td>{c.id_componente}</td>
                <td>{c.nombre}</td>
                <td>{c.porcentaje}</td>
              </tr>
            ))}
            {componentes.length === 0 && <tr><td colSpan={3}>No hay componentes registrados</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
export default Componentes;
