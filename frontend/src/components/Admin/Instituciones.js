import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/Instituciones.css";

function Instituciones() {
  const [instituciones, setInstituciones] = useState([]);
  const [form, setForm] = useState({ nombre_inst: "", jornada: "", dir_principal: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [editId, setEditId] = useState(null);
  const [editForm, setEditForm] = useState({ nombre_inst: "", jornada: "", dir_principal: "" });

  useEffect(() => {
    cargarInstituciones();
  }, []);

  function cargarInstituciones() {
    axios.get("http://localhost:8000/instituciones")
      .then(r => setInstituciones(r.data))
      .catch(() => setError("Error al cargar instituciones"));
  }

  function agregarInstitucion(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    
    if (!form.nombre_inst.trim()) {
      setError("El nombre es obligatorio");
      return;
    }
    
    axios.post("http://localhost:8000/instituciones", form)
      .then(() => {
        setForm({ nombre_inst: "", jornada: "", dir_principal: "" });
        setSuccess("Institución agregada correctamente");
        setTimeout(() => setSuccess(""), 3000);
        cargarInstituciones();
      })
      .catch(err => {
        const mensaje = err.response?.data?.detail || "No se pudo agregar la institución";
        setError(mensaje);
      });
  }

  function eliminarInstitucion(id) {
    if (!window.confirm("¿Estás seguro de que deseas eliminar esta institución?")) {
      return;
    }
    
    axios.delete(`http://localhost:8000/instituciones/${id}`)
      .then(() => {
        setSuccess("Institución eliminada correctamente");
        setTimeout(() => setSuccess(""), 3000);
        cargarInstituciones();
      })
      .catch(err => {
        const mensaje = err.response?.data?.detail || "Error al eliminar";
        setError(mensaje);
      });
  }

  function activarEdicion(inst) {
    setEditId(inst.id_institucion);
    setEditForm({
      nombre_inst: inst.nombre_inst,
      jornada: inst.jornada,
      dir_principal: inst.dir_principal
    });
    setError("");
    setSuccess("");
  }

  function handleEditChange(e) {
    setEditForm({ ...editForm, [e.target.name]: e.target.value });
  }

  function guardarEdicion(id) {
    if (!editForm.nombre_inst.trim()) {
      setError("El nombre es obligatorio");
      return;
    }
    
    axios.put(`http://localhost:8000/instituciones/${id}`, editForm)
      .then(() => {
        setEditId(null);
        setEditForm({ nombre_inst: "", jornada: "", dir_principal: "" });
        setSuccess("Institución actualizada correctamente");
        setTimeout(() => setSuccess(""), 3000);
        cargarInstituciones();
      })
      .catch(err => {
        const mensaje = err.response?.data?.detail || "No se pudo editar la institución";
        setError(mensaje);
      });
  }

  function cancelarEdicion() {
    setEditId(null);
    setEditForm({ nombre_inst: "", jornada: "", dir_principal: "" });
    setError("");
  }

  return (
    <div className="instituciones-panel">
      <h2>Invitar Institución al Programa</h2>
      
      <form className="instituciones-form" onSubmit={agregarInstitucion}>
        <input
          type="text"
          name="nombre_inst"
          placeholder="Nombre Institución"
          value={form.nombre_inst}
          onChange={e => setForm({ ...form, nombre_inst: e.target.value })}
          required
        />
        <input
          type="text"
          name="jornada"
          placeholder="Jornada"
          value={form.jornada}
          onChange={e => setForm({ ...form, jornada: e.target.value })}
        />
        <input
          type="text"
          name="dir_principal"
          placeholder="Dirección Principal"
          value={form.dir_principal}
          onChange={e => setForm({ ...form, dir_principal: e.target.value })}
        />
        <button type="submit" className="instituciones-btn">Invitar Institución</button>
      </form>
      
      {error && <div style={{ color: "#a11", padding: "10px", background: "#ffefef", borderRadius: "4px", marginBottom: "10px" }}>❌ {error}</div>}
      {success && <div style={{ color: "#237327", padding: "10px", background: "#eaffea", borderRadius: "4px", marginBottom: "10px" }}>✓ {success}</div>}
      
      <table className="instituciones-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>NOMBRE</th>
            <th>JORNADA</th>
            <th>DIRECCIÓN</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {instituciones.map(inst => (
            <tr key={inst.id_institucion}>
              <td>{inst.id_institucion}</td>
              <td>
                {editId === inst.id_institucion ? (
                  <input
                    type="text"
                    name="nombre_inst"
                    value={editForm.nombre_inst}
                    onChange={handleEditChange}
                    style={{ width: "100%" }}
                  />
                ) : (
                  inst.nombre_inst
                )}
              </td>
              <td>
                {editId === inst.id_institucion ? (
                  <input
                    type="text"
                    name="jornada"
                    value={editForm.jornada}
                    onChange={handleEditChange}
                    style={{ width: "100%" }}
                  />
                ) : (
                  inst.jornada || "-"
                )}
              </td>
              <td>
                {editId === inst.id_institucion ? (
                  <input
                    type="text"
                    name="dir_principal"
                    value={editForm.dir_principal}
                    onChange={handleEditChange}
                    style={{ width: "100%" }}
                  />
                ) : (
                  inst.dir_principal || "-"
                )}
              </td>
              <td>
                {editId === inst.id_institucion ? (
                  <>
                    <button className="btn-editar" onClick={() => guardarEdicion(inst.id_institucion)}>
                      Guardar
                    </button>
                    <button className="btn-cancelar" onClick={cancelarEdicion}>
                      Cancelar
                    </button>
                  </>
                ) : (
                  <>
                    <button className="btn-editar" onClick={() => activarEdicion(inst)}>
                      Editar
                    </button>
                    <button className="btn-eliminar" onClick={() => eliminarInstitucion(inst.id_institucion)}>
                      Eliminar
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
          {instituciones.length === 0 &&
            <tr><td colSpan={5} style={{ textAlign: "center", color: "#999" }}>No hay instituciones registradas</td></tr>
          }
        </tbody>
      </table>
    </div>
  );
}

export default Instituciones;
