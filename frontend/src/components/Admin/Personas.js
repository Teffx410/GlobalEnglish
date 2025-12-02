import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function Personas() {
  const [personas, setPersonas] = useState([]);
  const [form, setForm] = useState({
    tipo_doc: "",
    num_documento: "",
    nombre: "",
    telefono: "",
    correo: "",
    rol: "TUTOR",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [editId, setEditId] = useState(null);
  const [editForm, setEditForm] = useState({
    tipo_doc: "",
    num_documento: "",
    nombre: "",
    telefono: "",
    correo: "",
    rol: "TUTOR",
  });

  const rolActual = localStorage.getItem("rol") || "SIN_ROL";
  const esAdmin = rolActual === "ADMINISTRADOR";
  const esAdministrativo = rolActual === "ADMINISTRATIVO";

  useEffect(() => {
    cargarPersonas();
  }, []);

  function cargarPersonas() {
    setError("");
    axios
      .get("http://localhost:8000/personas")
      .then((r) => {
        const lista = r.data || [];
        // ADMIN ve a todos, ADMINISTRATIVO solo tutores
        const visibles = esAdmin ? lista : lista.filter((p) => p.rol === "TUTOR");
        setPersonas(visibles);
      })
      .catch(() => setError("Error al cargar personas"));
  }

  function agregarPersona(e) {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!form.tipo_doc || !form.num_documento || !form.nombre || !form.correo) {
      setError("Todos los campos son obligatorios");
      return;
    }

    let rolAEnviar = form.rol;

    // El ADMINISTRATIVO solo puede crear tutores
    if (esAdministrativo) {
      rolAEnviar = "TUTOR";
    }

    const payload = { ...form, rol: rolAEnviar };

    axios
      .post("http://localhost:8000/personas", payload)
      .then(() => {
        setForm({
          tipo_doc: "",
          num_documento: "",
          nombre: "",
          telefono: "",
          correo: "",
          rol: "TUTOR",
        });
        setSuccess("Persona registrada correctamente");
        setTimeout(() => setSuccess(""), 3000);
        cargarPersonas();
      })
      .catch((err) => {
        const mensaje = err.response?.data?.detail || "No se pudo registrar la persona";
        setError(mensaje);
      });
  }

  function eliminarPersona(id_persona) {
    if (!window.confirm("¿Estás seguro de que deseas eliminar esta persona?")) {
      return;
    }

    axios
      .delete(`http://localhost:8000/personas/${id_persona}`)
      .then(() => {
        setSuccess("Persona eliminada correctamente");
        setTimeout(() => setSuccess(""), 3000);
        cargarPersonas();
      })
      .catch((err) => {
        const mensaje = err.response?.data?.detail || "Error al eliminar";
        setError(mensaje);
      });
  }

  function activarEdicion(persona) {
    setEditId(persona.id_persona);
    setEditForm({
      tipo_doc: persona.tipo_doc,
      num_documento: persona.num_documento,
      nombre: persona.nombre,
      telefono: persona.telefono,
      correo: persona.correo,
      rol: persona.rol,
    });
    setError("");
  }

  function handleEditChange(e) {
    setEditForm({ ...editForm, [e.target.name]: e.target.value });
  }

  function guardarEdicion(id_persona) {
    if (
      !editForm.tipo_doc ||
      !editForm.num_documento ||
      !editForm.nombre ||
      !editForm.correo
    ) {
      setError("Todos los campos son obligatorios");
      return;
    }

    let rolAEnviar = editForm.rol;

    // ADMINISTRATIVO solo puede dejar/poner TUTOR
    if (esAdministrativo) {
      rolAEnviar = "TUTOR";
    }

    const payload = { ...editForm, rol: rolAEnviar };

    axios
      .put(`http://localhost:8000/personas/${id_persona}`, payload)
      .then(() => {
        setEditId(null);
        setEditForm({
          tipo_doc: "",
          num_documento: "",
          nombre: "",
          telefono: "",
          correo: "",
          rol: "TUTOR",
        });
        setSuccess("Persona actualizada correctamente");
        setTimeout(() => setSuccess(""), 3000);
        cargarPersonas();
      })
      .catch((err) => {
        const mensaje = err.response?.data?.detail || "No se pudo editar la persona";
        setError(mensaje);
      });
  }

  function cancelarEdicion() {
    setEditId(null);
    setEditForm({
      tipo_doc: "",
      num_documento: "",
      nombre: "",
      telefono: "",
      correo: "",
      rol: "TUTOR",
    });
    setError("");
  }

  // Solo ADMIN y ADMINISTRATIVO pueden entrar
  if (!esAdmin && !esAdministrativo) {
    return (
      <div className="sedes-panel">
        <h2>Personas</h2>
        <p>No tienes permisos para gestionar personas.</p>
      </div>
    );
  }

  return (
    <div className="sedes-panel">
      <h2>Registrar Persona</h2>

      <form className="sedes-form" onSubmit={agregarPersona}>
        <select
          name="tipo_doc"
          value={form.tipo_doc}
          onChange={(e) => setForm({ ...form, tipo_doc: e.target.value })}
          required
        >
          <option value="">Tipo Doc *</option>
          <option value="CC">C.C.</option>
          <option value="TI">T.I.</option>
          <option value="CE">C.E.</option>
          <option value="PASS">Pasaporte</option>
        </select>

        <input
          type="text"
          name="num_documento"
          placeholder="Número de Documento *"
          value={form.num_documento}
          onChange={(e) => setForm({ ...form, num_documento: e.target.value })}
          required
        />

        <input
          type="text"
          name="nombre"
          placeholder="Nombre completo *"
          value={form.nombre}
          onChange={(e) => setForm({ ...form, nombre: e.target.value })}
          required
        />

        <input
          type="text"
          name="telefono"
          placeholder="Teléfono"
          value={form.telefono}
          onChange={(e) => setForm({ ...form, telefono: e.target.value })}
        />

        <input
          type="email"
          name="correo"
          placeholder="Correo *"
          value={form.correo}
          onChange={(e) => setForm({ ...form, correo: e.target.value })}
          required
        />

        {esAdmin ? (
          <select
            name="rol"
            value={form.rol}
            onChange={(e) => setForm({ ...form, rol: e.target.value })}
            required
          >
            <option value="TUTOR">TUTOR</option>
            <option value="ADMINISTRATIVO">ADMINISTRATIVO</option>
            <option value="ADMINISTRADOR">ADMINISTRADOR</option>
          </select>
        ) : (
          <input
            type="text"
            value="TUTOR"
            disabled
            style={{ background: "#f4f4f4", cursor: "not-allowed" }}
          />
        )}

        <button type="submit" className="sedes-btn">
          Registrar
        </button>
      </form>

      {error && (
        <div
          style={{
            color: "#a11",
            padding: "10px",
            background: "#ffefef",
            borderRadius: "4px",
            marginBottom: "10px",
          }}
        >
          ❌ {error}
        </div>
      )}
      {success && (
        <div
          style={{
            color: "#237327",
            padding: "10px",
            background: "#eaffea",
            borderRadius: "4px",
            marginBottom: "10px",
          }}
        >
          ✓ {success}
        </div>
      )}

      <h3 style={{ marginTop: 20, marginBottom: 10 }}>
        {esAdmin ? "Listado de Personas" : "Listado de Tutores"}
      </h3>

      <table className="sedes-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Tipo Doc</th>
            <th>Número Documento</th>
            <th>Nombre</th>
            <th>Teléfono</th>
            <th>Correo</th>
            <th>Rol</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {personas.map((persona) => (
            <tr key={persona.id_persona}>
              <td>{persona.id_persona}</td>

              <td>
                {editId === persona.id_persona ? (
                  <select
                    name="tipo_doc"
                    value={editForm.tipo_doc}
                    onChange={handleEditChange}
                    style={{ width: "100%" }}
                  >
                    <option value="CC">C.C.</option>
                    <option value="TI">T.I.</option>
                    <option value="CE">C.E.</option>
                    <option value="PASS">Pasaporte</option>
                  </select>
                ) : (
                  persona.tipo_doc
                )}
              </td>

              <td>
                {editId === persona.id_persona ? (
                  <input
                    type="text"
                    name="num_documento"
                    value={editForm.num_documento}
                    onChange={handleEditChange}
                    style={{ width: "100%" }}
                  />
                ) : (
                  persona.num_documento
                )}
              </td>

              <td>
                {editId === persona.id_persona ? (
                  <input
                    type="text"
                    name="nombre"
                    value={editForm.nombre}
                    onChange={handleEditChange}
                    style={{ width: "100%" }}
                  />
                ) : (
                  persona.nombre
                )}
              </td>

              <td>
                {editId === persona.id_persona ? (
                  <input
                    type="text"
                    name="telefono"
                    value={editForm.telefono}
                    onChange={handleEditChange}
                    style={{ width: "100%" }}
                  />
                ) : (
                  persona.telefono
                )}
              </td>

              <td>
                {editId === persona.id_persona ? (
                  <input
                    type="email"
                    name="correo"
                    value={editForm.correo}
                    onChange={handleEditChange}
                    style={{ width: "100%" }}
                  />
                ) : (
                  persona.correo
                )}
              </td>

              <td>
                {editId === persona.id_persona ? (
                  esAdmin ? (
                    <select
                      name="rol"
                      value={editForm.rol}
                      onChange={handleEditChange}
                    >
                      <option value="TUTOR">TUTOR</option>
                      <option value="ADMINISTRATIVO">ADMINISTRATIVO</option>
                      <option value="ADMINISTRADOR">ADMINISTRADOR</option>
                    </select>
                  ) : (
                    "TUTOR"
                  )
                ) : (
                  persona.rol
                )}
              </td>

              <td>
                {editId === persona.id_persona ? (
                  <>
                    <button
                      className="btn-editar"
                      onClick={() => guardarEdicion(persona.id_persona)}
                    >
                      Guardar
                    </button>
                    <button className="btn-cancelar" onClick={cancelarEdicion}>
                      Cancelar
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      className="btn-editar"
                      onClick={() => activarEdicion(persona)}
                    >
                      Editar
                    </button>
                    <button
                      className="btn-eliminar"
                      onClick={() => eliminarPersona(persona.id_persona)}
                    >
                      Eliminar
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}

          {personas.length === 0 && (
            <tr>
              <td colSpan={8} style={{ textAlign: "center", color: "#999" }}>
                No hay personas registradas
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default Personas;
