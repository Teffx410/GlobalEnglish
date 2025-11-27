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
<<<<<<< HEAD
=======
  const [error, setError] = useState("");
>>>>>>> main

  useEffect(() => {
    cargarUsuarios();
    cargarPersonas();
  }, []);

  function cargarUsuarios() {
<<<<<<< HEAD
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
=======
    axios
      .get("http://localhost:8000/usuarios")
      .then((r) => {
        console.log("RESP USUARIOS:", r.data);
        // Asumimos que r.data es un array directo.
        // Si tu backend cambia a { usuarios: [...] }, aquí se ajusta.
        const lista = Array.isArray(r.data) ? r.data : r.data.usuarios || [];
        setUsuarios(lista);
        setError("");
      })
      .catch((err) => {
        console.error("Error al cargar usuarios", err.response?.data || err.message);
        setUsuarios([]);
        setError("Error al cargar usuarios");
      });
  }

  function cargarPersonas() {
    axios
      .get("http://localhost:8000/personas")
      .then((r) => {
        console.log("RESP PERSONAS:", r.data);
        const lista = Array.isArray(r.data) ? r.data : r.data.personas || [];
        setPersonas(lista);
        setError("");
      })
      .catch((err) => {
        console.error("Error al cargar personas", err.response?.data || err.message);
        setPersonas([]);
        setError("Error al cargar personas");
      });
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  }

  function agregarUsuario(e) {
    e.preventDefault();

    // Validación simple para evitar problemas con NOT NULL en la BD
    if (!form.nombre_user.trim()) {
      setError("El nombre de usuario es obligatorio");
      setMsg("");
      return;
    }

    if (!form.id_persona) {
      setError("Debe seleccionar una persona");
      setMsg("");
      return;
    }

    if (!form.contrasena.trim()) {
      setError("La contraseña es obligatoria");
      setMsg("");
      return;
    }

    console.log("Enviando usuario:", form);

    axios
      .post("http://localhost:8000/usuarios", form)
      .then((r) => {
        console.log("RESP CREAR USUARIO:", r.data);
        setMsg(
          "Usuario creado. Contraseña temporal: " +
            (r.data.clave_generada || form.contrasena || "N/A")
        );
        setError("");
        cargarUsuarios();
        setForm({ nombre_user: "", contrasena: "", id_persona: "" });
      })
      .catch((err) => {
        console.error("Error al crear usuario", err.response?.data || err.message);
        setError("Error al crear usuario");
        setMsg("");
      });
  }

  return (
    <div className="instituciones-panel">
      <h2>Registrar Usuario (Persona existente)</h2>

      <form className="instituciones-form" onSubmit={agregarUsuario}>
        <input
          className="aulas-form-input"
          type="text"
          name="nombre_user"
          placeholder="Nombre de usuario"
          value={form.nombre_user}
          onChange={handleFormChange}
          required
        />

        <input
          className="aulas-form-input"
          type="password"
          name="contrasena"
          placeholder="Contraseña"
          value={form.contrasena}
          onChange={handleFormChange}
          required
        />

        <select
          className="aulas-form-input"
          name="id_persona"
          value={form.id_persona}
          onChange={handleFormChange}
          required
        >
          <option value="">Persona</option>
          {personas.map((p) => (
            <option key={p.id_persona} value={p.id_persona}>
              {p.nombre} ({p.correo}) - {p.rol}
            </option>
          ))}
        </select>

        <button type="submit" className="aulas-btn">
          Registrar Usuario
        </button>
      </form>

      {msg && (
        <div style={{ color: "green", marginBottom: "10px" }}>
          {msg}
        </div>
      )}
      {error && (
        <div style={{ color: "red", marginBottom: "10px" }}>
          {error}
        </div>
      )}

>>>>>>> main
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
<<<<<<< HEAD
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
=======
              <th>Usuario</th>
              <th>Correo</th>
              <th>Persona</th>
              <th>Rol</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map((u) => {
              // "JOIN" en frontend: buscamos la persona de ese usuario
              const persona = personas.find(
                (p) => Number(p.id_persona) === Number(u.id_persona)
              );

              return (
                <tr key={u.nombre_user}>
                  <td>{u.nombre_user}</td>
                  <td>{persona?.correo || "—"}</td>
                  <td>{persona?.nombre || "—"}</td>
                  <td>{persona?.rol || "—"}</td>
                </tr>
              );
            })}
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
export default Usuarios;
