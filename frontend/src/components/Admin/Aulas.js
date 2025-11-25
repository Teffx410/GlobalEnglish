import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css"; // CSS global

function Aulas() {
  const [aulas, setAulas] = useState([]);
  const [instituciones, setInstituciones] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [form, setForm] = useState({
    id_institucion: "",
    id_sede: "",
    grado: ""
  });
  const [error, setError] = useState("");
  const [editId, setEditId] = useState(null);
  const [editForm, setEditForm] = useState({
    id_institucion: "",
    id_sede: "",
    grado: ""
  });
  const [editSedes, setEditSedes] = useState([]);

  useEffect(() => {
    cargarAulas();
    cargarInstituciones();
  }, []);

  function cargarAulas() {
    axios.get("http://localhost:8000/aulas")
      .then(r => setAulas(r.data))
      .catch(() => setError("Error al cargar aulas"));
  }

  function cargarInstituciones() {
    axios.get("http://localhost:8000/instituciones")
      .then(r => setInstituciones(r.data))
      .catch(() => setError("Error al cargar instituciones"));
  }

  function cargarSedes(id_institucion) {
    if (!id_institucion) {
      setSedes([]);
      return;
    }
    axios.get("http://localhost:8000/sedes")
      .then(r => {
        setSedes(r.data.filter(s => s.id_institucion === Number(id_institucion)));
      })
      .catch(() => setError("Error al cargar sedes"));
  }

  function cargarEditSedes(id_institucion) {
    axios.get("http://localhost:8000/sedes")
      .then(r => {
        setEditSedes(r.data.filter(s => s.id_institucion === Number(id_institucion)));
      })
      .catch(() => setError("Error al cargar sedes"));
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    if (name === "id_institucion") {
      setForm(f => ({ ...f, id_sede: "" }));
      cargarSedes(value);
    }
  }

  function agregarAula(e) {
    e.preventDefault();
    if (!form.id_institucion || !form.id_sede || !form.grado) {
      setError("Todos los campos son obligatorios");
      return;
    }
    axios.post("http://localhost:8000/aulas", form)
      .then(() => {
        setForm({ id_institucion: "", id_sede: "", grado: "" });
        setError("");
        cargarAulas();
      })
      .catch(() => setError("No se pudo agregar el aula"));
  }

  function eliminarAula(id) {
    axios.delete(`http://localhost:8000/aulas/${id}`)
      .then(() => cargarAulas())
      .catch(() => setError("Error al eliminar aula"));
  }

  function activarEdicion(aula) {
    setEditId(aula.id_aula);
    setEditForm({
      id_institucion: aula.id_institucion,
      id_sede: aula.id_sede,
      grado: aula.grado
    });
    cargarEditSedes(aula.id_institucion);
  }

  function handleEditChange(e) {
    const { name, value } = e.target;
    setEditForm({ ...editForm, [name]: value });
    if (name === "id_institucion") {
      setEditForm(f => ({ ...f, id_sede: "" }));
      cargarEditSedes(value);
    }
  }

  function guardarEdicion(id) {
    axios.put(`http://localhost:8000/aulas/${id}`, editForm)
      .then(() => {
        setEditId(null);
        setEditForm({ id_institucion: "", id_sede: "", grado: "" });
        cargarAulas();
      })
      .catch(() => setError("No se pudo editar el aula"));
  }

  function cancelarEdicion() {
    setEditId(null);
    setEditForm({ id_institucion: "", id_sede: "", grado: "" });
    setEditSedes([]);
  }

  return (
    <div className="aulas-panel">
      <h2 style={{marginBottom: "16px"}}>Ingresar Aula</h2>
      <form className="aulas-form" onSubmit={agregarAula}>
        <select
          className="aulas-form-input"
          name="id_institucion"
          value={form.id_institucion}
          onChange={handleFormChange}
          required
        >
          <option value="">Institución</option>
          {instituciones.map(i => (
            <option key={i.id_institucion} value={i.id_institucion}>{i.nombre_inst}</option>
          ))}
        </select>
        <select
          className="aulas-form-input"
          name="id_sede"
          value={form.id_sede}
          onChange={e => setForm({ ...form, id_sede: e.target.value })}
          required
          disabled={!form.id_institucion}
        >
          <option value="">Sede</option>
          {sedes.map(s => (
            <option key={s.id_sede} value={s.id_sede}>{s.direccion} ({s.id_sede})</option>
          ))}
        </select>
        <input
          className="aulas-form-input"
          type="text"
          name="grado"
          placeholder="Grado"
          value={form.grado}
          onChange={e => setForm({ ...form, grado: e.target.value })}
          required
        />
        <button type="submit" className="aulas-btn">Agregar Aula</button>
      </form>
      {error && <div style={{ color: "red", marginBottom: "10px" }}>{error}</div>}
      <table className="aulas-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Institución</th>
            <th>Sede</th>
            <th>Grado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {aulas.map(aula => (
            <tr key={aula.id_aula}>
              <td>{aula.id_aula}</td>
              <td>
                {editId === aula.id_aula ? (
                  <select
                    className="aulas-form-input"
                    name="id_institucion"
                    value={editForm.id_institucion}
                    onChange={handleEditChange}
                    required
                  >
                    <option value="">Institución</option>
                    {instituciones.map(i => (
                      <option key={i.id_institucion} value={i.id_institucion}>{i.nombre_inst}</option>
                    ))}
                  </select>
                ) : (
                  instituciones.find(i => i.id_institucion === aula.id_institucion)?.nombre_inst || aula.id_institucion
                )}
              </td>
              <td>
                {editId === aula.id_aula ? (
                  <select
                    className="aulas-form-input"
                    name="id_sede"
                    value={editForm.id_sede}
                    onChange={handleEditChange}
                    required
                    disabled={!editForm.id_institucion}
                  >
                    <option value="">Sede</option>
                    {editSedes.map(s => (
                      <option key={s.id_sede} value={s.id_sede}>{s.direccion} ({s.id_sede})</option>
                    ))}
                  </select>
                ) : (
                  sedes.find(s => s.id_institucion === aula.id_institucion && s.id_sede === aula.id_sede)?.direccion || aula.id_sede
                )}
              </td>
              <td>
                {editId === aula.id_aula ? (
                  <input
                    className="aulas-form-input"
                    type="text"
                    name="grado"
                    value={editForm.grado}
                    onChange={handleEditChange}
                  />
                ) : (
                  aula.grado
                )}
              </td>
              <td>
                {editId === aula.id_aula ? (
                  <>
                    <button className="btn-editar" type="button" onClick={() => guardarEdicion(aula.id_aula)}>Guardar</button>
                    <button className="btn-cancelar" type="button" onClick={cancelarEdicion}>Cancelar</button>
                  </>
                ) : (
                  <>
                    <button className="btn-editar" type="button" onClick={() => activarEdicion(aula)}>Editar</button>
                    <button className="btn-eliminar" type="button" onClick={() => eliminarAula(aula.id_aula)}>Eliminar</button>
                  </>
                )}
              </td>
            </tr>
          ))}
          {aulas.length === 0 &&
            <tr><td colSpan={5}>No hay aulas registradas</td></tr>
          }
        </tbody>
      </table>
    </div>
  );
}

export default Aulas;
