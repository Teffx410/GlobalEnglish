import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function Sedes() {
  const [sedes, setSedes] = useState([]);
  const [instituciones, setInstituciones] = useState([]);
  const [form, setForm] = useState({ id_institucion: "", direccion: "", es_principal: "N" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [editId, setEditId] = useState(null);
  const [editForm, setEditForm] = useState({ id_institucion: "", direccion: "", es_principal: "N" });

  useEffect(() => {
    cargarSedes();
    cargarInstituciones();
  }, []);

  function cargarSedes() {
    axios.get("http://localhost:8000/sedes")
      .then(r => setSedes(r.data))
      .catch(() => setError("Error al cargar sedes"));
  }

  function cargarInstituciones() {
    axios.get("http://localhost:8000/instituciones")
      .then(r => setInstituciones(r.data))
      .catch(() => setError("Error al cargar instituciones"));
  }

  function agregarSede(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    
    if (!form.direccion.trim() || !form.id_institucion) {
      setError("Todos los campos son obligatorios");
      return;
    }
    
    axios.post("http://localhost:8000/sedes", {
      id_institucion: parseInt(form.id_institucion),
      direccion: form.direccion,
      es_principal: form.es_principal
    })
      .then(() => {
        setForm({ id_institucion: "", direccion: "", es_principal: "N" });
        setSuccess("Sede agregada correctamente");
        setTimeout(() => setSuccess(""), 3000);
        cargarSedes();
      })
      .catch(err => {
        const mensaje = err.response?.data?.detail || "No se pudo agregar la sede";
        setError(mensaje);
      });
  }

  function eliminarSede(id_institucion, id_sede) {
    if (!window.confirm("¿Estás seguro de que deseas eliminar esta sede?")) {
      return;
    }
    
    axios.delete(`http://localhost:8000/sedes/${id_institucion}/${id_sede}`)
      .then(() => {
        setSuccess("Sede eliminada correctamente");
        setTimeout(() => setSuccess(""), 3000);
        cargarSedes();
      })
      .catch(err => {
        const mensaje = err.response?.data?.detail || "Error al eliminar";
        setError(mensaje);
      });
  }


  function activarEdicion(sede) {
    setEditId(sede.id_sede);
    setEditForm({
      id_institucion: sede.id_institucion,
      direccion: sede.direccion,
      es_principal: sede.es_principal
    });
    setError("");
  }

  function handleEditChange(e) {
    setEditForm({ ...editForm, [e.target.name]: e.target.value });
  }

  function guardarEdicion(id) {
    if (!editForm.direccion.trim() || !editForm.id_institucion) {
      setError("Todos los campos son obligatorios");
      return;
    }
    
    axios.put(`http://localhost:8000/sedes/${id}`, {
      id_institucion: parseInt(editForm.id_institucion),
      direccion: editForm.direccion,
      es_principal: editForm.es_principal
    })
      .then(() => {
        setEditId(null);
        setEditForm({ id_institucion: "", direccion: "", es_principal: "N" });
        setSuccess("Sede actualizada correctamente");
        setTimeout(() => setSuccess(""), 3000);
        cargarSedes();
      })
      .catch(err => {
        const mensaje = err.response?.data?.detail || "No se pudo editar la sede";
        setError(mensaje);
      });
  }

  function cancelarEdicion() {
    setEditId(null);
    setEditForm({ id_institucion: "", direccion: "", es_principal: "N" });
    setError("");
  }

  return (
    <div className="sedes-panel">
      <h2>Ingresar Sede</h2>
      <form className="sedes-form" onSubmit={agregarSede}>
        <select
          name="id_institucion"
          value={form.id_institucion}
          onChange={e => setForm({ ...form, id_institucion: e.target.value })}
          required
        >
          <option value="">Seleccione institución</option>
          {instituciones.map(inst => (
            <option value={inst.id_institucion} key={inst.id_institucion}>
              {inst.nombre_inst}
            </option>
          ))}
        </select>
        <input
          type="text"
          name="direccion"
          placeholder="Dirección"
          value={form.direccion}
          onChange={e => setForm({ ...form, direccion: e.target.value })}
          required
        />
        <select
          name="es_principal"
          value={form.es_principal}
          onChange={e => setForm({ ...form, es_principal: e.target.value })}
        >
          <option value="N">No principal</option>
          <option value="S">Principal</option>
        </select>
        <button type="submit" className="sedes-btn">Agregar Sede</button>
      </form>
      
      {error && <div style={{ color: "#a11", padding: "10px", background: "#ffefef", borderRadius: "4px", marginBottom: "10px" }}>❌ {error}</div>}
      {success && <div style={{ color: "#237327", padding: "10px", background: "#eaffea", borderRadius: "4px", marginBottom: "10px" }}>✓ {success}</div>}
      
      <table className="sedes-table">
        <thead>
          <tr>
            <th>ID_SEDE</th>
            <th>INSTITUCIÓN</th>
            <th>DIRECCIÓN</th>
            <th>ES_PRINCIPAL</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {sedes.map(sede => {
            const institucion = instituciones.find(i => i.id_institucion === sede.id_institucion);
            return (
              <tr key={sede.id_sede}>
                <td>{sede.id_sede}</td>
                <td>
                  {editId === sede.id_sede ? (
                    <select
                      name="id_institucion"
                      value={editForm.id_institucion}
                      onChange={handleEditChange}
                      style={{ width: "100%" }}
                    >
                      {instituciones.map(inst => (
                        <option value={inst.id_institucion} key={inst.id_institucion}>
                          {inst.nombre_inst}
                        </option>
                      ))}
                    </select>
                  ) : (
                    institucion?.nombre_inst || "N/A"
                  )}
                </td>
                <td>
                  {editId === sede.id_sede ? (
                    <input
                      type="text"
                      name="direccion"
                      value={editForm.direccion}
                      onChange={handleEditChange}
                      style={{ width: "100%" }}
                    />
                  ) : (
                    sede.direccion
                  )}
                </td>
                <td>
                  {editId === sede.id_sede ? (
                    <select
                      name="es_principal"
                      value={editForm.es_principal}
                      onChange={handleEditChange}
                    >
                      <option value="N">No principal</option>
                      <option value="S">Principal</option>
                    </select>
                  ) : (
                    sede.es_principal === "S" ? "Principal" : "No principal"
                  )}
                </td>
                <td>
                  {editId === sede.id_sede ? (
                    <>
                      <button className="btn-editar" onClick={() => guardarEdicion(sede.id_sede)}>
                        Guardar
                      </button>
                      <button className="btn-cancelar" onClick={cancelarEdicion}>
                        Cancelar
                      </button>
                    </>
                  ) : (
                    <>
                      <button className="btn-editar" onClick={() => activarEdicion(sede)}>
                        Editar
                      </button>
                      <button className="btn-eliminar" onClick={() => eliminarSede(sede.id_institucion, sede.id_sede)}>
                        Eliminar
                      </button>
                    </>
                  )}
                </td>
              </tr>
            );
          })}
          {sedes.length === 0 &&
            <tr><td colSpan={5} style={{ textAlign: "center", color: "#999" }}>No hay sedes registradas</td></tr>
          }
        </tbody>
      </table>
    </div>
  );
}

export default Sedes;
