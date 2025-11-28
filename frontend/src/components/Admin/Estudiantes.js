import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function Estudiantes() {
  const [estudiantes, setEstudiantes] = useState([]);
  const [form, setForm] = useState({
    tipo_documento: "",
    num_documento: "",
    nombres: "",
    apellidos: "",
    telefono: "",
    fecha_nacimiento: "",
    correo: ""
  });
  const [error, setError] = useState("");
  const [editId, setEditId] = useState(null);
  const [editForm, setEditForm] = useState({
    tipo_documento: "",
    num_documento: "",
    nombres: "",
    apellidos: "",
    telefono: "",
    fecha_nacimiento: "",
    correo: ""
  });

  useEffect(() => {
    cargarEstudiantes();
  }, []);

  function cargarEstudiantes() {
    axios.get("http://localhost:8000/estudiantes")
      .then(r => setEstudiantes(r.data))
      .catch(() => setError("Error al cargar estudiantes"));
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    setError("");
  }

  function agregarEstudiante(e) {
    e.preventDefault();
    setError("");
    if (!form.num_documento || !form.nombres) {
      setError("Documento y nombres son obligatorios");
      return;
    }
    axios.post("http://localhost:8000/estudiantes", form)
      .then(() => {
        setForm({
          tipo_documento: "",
          num_documento: "",
          nombres: "",
          apellidos: "",
          telefono: "",
          fecha_nacimiento: "",
          correo: ""
        });
        setError("");
        cargarEstudiantes();
      })
      .catch(err => {
        if (err.response && err.response.data && err.response.data.detail) {
          setError(err.response.data.detail);
        } else {
          setError("No se pudo agregar el estudiante");
        }
      });
  }

  function eliminarEstudiante(id) {
    axios.delete(`http://localhost:8000/estudiantes/${id}`)
      .then(() => cargarEstudiantes())
      .catch(() => setError("Error al eliminar estudiante"));
  }

  function activarEdicion(est) {
    setEditId(est.id_estudiante);
    setEditForm({
      ...est,
      fecha_nacimiento: est.fecha_nacimiento ? est.fecha_nacimiento.slice(0, 10) : ""
    });
    setError("");
  }

  function handleEditChange(e) {
    const { name, value } = e.target;
    setEditForm({ ...editForm, [name]: value });
    setError("");
  }

  function guardarEdicion(id) {
    setError("");
    axios.put(`http://localhost:8000/estudiantes/${id}`, editForm)
      .then(() => {
        setEditId(null);
        setEditForm({
          tipo_documento: "",
          num_documento: "",
          nombres: "",
          apellidos: "",
          telefono: "",
          fecha_nacimiento: "",
          correo: ""
        });
        cargarEstudiantes();
      })
      .catch(err => {
        if (err.response && err.response.data && err.response.data.detail) {
          setError(err.response.data.detail);
        } else {
          setError("No se pudo editar el estudiante");
        }
      });
  }

  function cancelarEdicion() {
    setEditId(null);
    setEditForm({
      tipo_documento: "",
      num_documento: "",
      nombres: "",
      apellidos: "",
      telefono: "",
      fecha_nacimiento: "",
      correo: ""
    });
    setError("");
  }

  return (
    <div className="instituciones-panel">
      <h2>Registrar Estudiante</h2>
      <form className="instituciones-form" onSubmit={agregarEstudiante}>
        <select
          className="aulas-form-input"
          name="tipo_documento"
          value={form.tipo_documento}
          onChange={handleFormChange}
        >
          <option value="">Tipo Doc</option>
          <option value="CC">C.C.</option>
          <option value="TI">T.I.</option>
          <option value="CE">C.E.</option>
          <option value="PASS">Pasaporte</option>
        </select>
        <input
          className="aulas-form-input"
          type="text"
          name="num_documento"
          placeholder="Documento"
          value={form.num_documento}
          onChange={handleFormChange}
          required
        />
        <input
          className="aulas-form-input"
          type="text"
          name="nombres"
          placeholder="Nombres"
          value={form.nombres}
          onChange={handleFormChange}
          required
        />
        <input
          className="aulas-form-input"
          type="text"
          name="apellidos"
          placeholder="Apellidos"
          value={form.apellidos}
          onChange={handleFormChange}
        />
        <input
          className="aulas-form-input"
          type="text"
          name="telefono"
          placeholder="Teléfono"
          value={form.telefono}
          onChange={handleFormChange}
        />
        <input
          className="aulas-form-input"
          type="date"
          name="fecha_nacimiento"
          placeholder="Fecha Nac."
          value={form.fecha_nacimiento}
          onChange={handleFormChange}
        />
        <input
          className="aulas-form-input"
          type="email"
          name="correo"
          placeholder="Correo"
          value={form.correo}
          onChange={handleFormChange}
        />
        <button type="submit" className="aulas-btn">Agregar Estudiante</button>
      </form>
      {error && <div style={{ color: "red", marginBottom: "10px" }}>{error}</div>}
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Tipo Doc</th>
              <th>Documento</th>
              <th>Nombres</th>
              <th>Apellidos</th>
              <th>Teléfono</th>
              <th>Fecha Nac.</th>
              <th>Correo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {estudiantes.map(est => (
              <tr key={est.id_estudiante}>
                <td>{est.id_estudiante}</td>
                <td>
                  {editId === est.id_estudiante ? (
                    <select
                      className="aulas-form-input"
                      name="tipo_documento"
                      value={editForm.tipo_documento}
                      onChange={handleEditChange}
                    >
                      <option value="">Tipo Doc</option>
                      <option value="CC">C.C.</option>
                      <option value="TI">T.I.</option>
                      <option value="CE">C.E.</option>
                      <option value="PASS">Pasaporte</option>
                    </select>
                  ) : (
                    est.tipo_documento
                  )}
                </td>
                <td>
                  {editId === est.id_estudiante ? (
                    <input className="aulas-form-input" type="text" name="num_documento" value={editForm.num_documento} onChange={handleEditChange} />
                  ) : (
                    est.num_documento
                  )}
                </td>
                <td>
                  {editId === est.id_estudiante ? (
                    <input className="aulas-form-input" type="text" name="nombres" value={editForm.nombres} onChange={handleEditChange} />
                  ) : (
                    est.nombres
                  )}
                </td>
                <td>
                  {editId === est.id_estudiante ? (
                    <input className="aulas-form-input" type="text" name="apellidos" value={editForm.apellidos} onChange={handleEditChange} />
                  ) : (
                    est.apellidos
                  )}
                </td>
                <td>
                  {editId === est.id_estudiante ? (
                    <input className="aulas-form-input" type="text" name="telefono" value={editForm.telefono} onChange={handleEditChange} />
                  ) : (
                    est.telefono
                  )}
                </td>
                <td>
                  {editId === est.id_estudiante ? (
                    <input className="aulas-form-input" type="date" name="fecha_nacimiento" value={editForm.fecha_nacimiento || ""} onChange={handleEditChange} />
                  ) : (
                    est.fecha_nacimiento
                  )}
                </td>
                <td>
                  {editId === est.id_estudiante ? (
                    <input className="aulas-form-input" type="email" name="correo" value={editForm.correo} onChange={handleEditChange} />
                  ) : (
                    est.correo
                  )}
                </td>
                <td>
                  {editId === est.id_estudiante ? (
                    <>
                      <button className="btn-editar" type="button" onClick={() => guardarEdicion(est.id_estudiante)}>Guardar</button>
                      <button className="btn-cancelar" type="button" onClick={cancelarEdicion}>Cancelar</button>
                    </>
                  ) : (
                    <>
                      <button className="btn-editar" type="button" onClick={() => activarEdicion(est)}>Editar</button>
                      <button className="btn-eliminar" type="button" onClick={() => eliminarEstudiante(est.id_estudiante)}>Eliminar</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
            {estudiantes.length === 0 &&
              <tr><td colSpan={9}>No hay estudiantes registrados</td></tr>
            }
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Estudiantes;
