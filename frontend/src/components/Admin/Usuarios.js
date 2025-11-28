import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function Usuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [personas, setPersonas] = useState([]);
  const [form, setForm] = useState({
    nombre_user: "",
    contrasena: "",
    id_persona: ""
  });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    cargarUsuarios();
    cargarPersonas();
  }, []);

  function cargarUsuarios() {
    axios.get("http://localhost:8000/usuarios").then(r => setUsuarios(r.data));
  }
  function cargarPersonas() {
    axios.get("http://localhost:8000/personas").then(r => setPersonas(r.data));
  }
  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  }
  function agregarUsuario(e) {
    e.preventDefault();
    axios.post("http://localhost:8000/usuarios", form)
      .then(r => {
        setMsg("Usuario creado. Contraseña temporal: " + (r.data.clave_generada || "N/A"));
        cargarUsuarios();
        setForm({ nombre_user: "", contrasena: "", id_persona: "" });
      })
      .catch(() => setMsg("Error al crear usuario"));
  }
  return (
    <div className="instituciones-panel">
      <h2>Registrar Usuario (Persona existente)</h2>
      <form className="instituciones-form" onSubmit={agregarUsuario}>
        <input className="aulas-form-input" type="text" name="nombre_user" placeholder="Nombre usuario" value={form.nombre_user} onChange={handleFormChange} required/>
        <input className="aulas-form-input" type="password" name="contrasena" placeholder="Contraseña (opcional)" value={form.contrasena} onChange={handleFormChange}/>
        <select className="aulas-form-input" name="id_persona" value={form.id_persona} onChange={handleFormChange} required>
          <option value="">Persona</option>
          {personas.map(p =>
            <option key={p.id_persona} value={p.id_persona}>
              {p.nombre} ({p.correo}) - {p.rol}
            </option>
          )}
        </select>
        <button type="submit" className="aulas-btn">Registrar Usuario</button>
      </form>
      {msg && <div style={{ color: "green", marginBottom: "10px" }}>{msg}</div>}
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>Usuario</th><th>Correo</th><th>Persona</th><th>Rol</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map(u => (
              <tr key={u.nombre_user}>
                <td>{u.nombre_user}</td>
                <td>{u.correo}</td>
                <td>{u.nombre}</td>
                <td>{u.rol}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
export default Usuarios;
