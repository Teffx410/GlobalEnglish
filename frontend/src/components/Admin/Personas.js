import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function Personas() {
  const [personas, setPersonas] = useState([]);
  const [form, setForm] = useState({
    tipo_doc: "",
    nombre: "",
    telefono: "",
    correo: "",
    rol: ""
  });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    cargarPersonas();
  }, []);

  function cargarPersonas() {
    axios.get("http://localhost:8000/personas").then(r => setPersonas(r.data));
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  }

  function agregarPersona(e) {
    e.preventDefault();
    axios.post("http://localhost:8000/personas", form)
      .then(r => {
        setMsg("Persona registrada (ID: " + r.data.id_persona + ")");
        cargarPersonas();
        setForm({ tipo_doc: "", nombre: "", telefono: "", correo: "", rol: "" });
      })
      .catch(() => setMsg("Error al registrar persona"));
  }

  return (
    <div className="instituciones-panel">
      <h2>Registrar Persona</h2>
      <form className="instituciones-form" onSubmit={agregarPersona}>
        <select className="aulas-form-input" name="tipo_doc" value={form.tipo_doc} onChange={handleFormChange} required>
          <option value="">Tipo Doc</option>
          <option value="CC">C.C.</option>
          <option value="TI">T.I.</option>
          <option value="CE">C.E.</option>
          <option value="PASS">Pasaporte</option>
        </select>
        <input className="aulas-form-input" type="text" name="nombre" placeholder="Nombre completo" value={form.nombre} onChange={handleFormChange} required/>
        <input className="aulas-form-input" type="text" name="telefono" placeholder="Teléfono" value={form.telefono} onChange={handleFormChange}/>
        <input className="aulas-form-input" type="email" name="correo" placeholder="Correo" value={form.correo} onChange={handleFormChange} required/>
        <select className="aulas-form-input" name="rol" value={form.rol} onChange={handleFormChange} required>
          <option value="">Rol</option>
          <option value="ADMINISTRADOR">Administrador</option>
          <option value="TUTOR">Tutor</option>
          <option value="OPERATIVO">Operativo</option>
          <option value="ESTUDIANTE">Estudiante</option>
        </select>
        <button type="submit" className="aulas-btn">Registrar Persona</button>
      </form>
      {msg && <div style={{ color: "green", marginBottom: "10px" }}>{msg}</div>}
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Tipo Doc</th>
              <th>Nombre</th>
              <th>Teléfono</th>
              <th>Correo</th>
              <th>Rol</th>
            </tr>
          </thead>
          <tbody>
            {personas.map(p => (
              <tr key={p.id_persona}>
                <td>{p.id_persona}</td>
                <td>{p.tipo_doc}</td>
                <td>{p.nombre}</td>
                <td>{p.telefono}</td>
                <td>{p.correo}</td>
                <td>{p.rol}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
export default Personas;
