// src/components/Admin/Instituciones.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function Instituciones() {
  const [instituciones, setInstituciones] = useState([]);
  const [form, setForm] = useState({
    nombre_inst: "",
    jornada: "",
    dir_principal: "",
    id_sede: "" // NUEVO: Número de sede inicial
  });

  const [editId, setEditId] = useState(null);
  const [editForm, setEditForm] = useState({
    nombre_inst: "",
    jornada: "",
    dir_principal: "",
  });

  const [error, setError] = useState("");

  useEffect(() => {
    cargarInstituciones();
  }, []);

  function cargarInstituciones() {
    axios
      .get("http://localhost:8000/instituciones")
      .then((r) => setInstituciones(r.data))
      .catch(() => setError("Error al cargar instituciones"));
  }

  // ===========================
  //  AGREGAR INSTITUCIÓN + SEDE
  // ===========================
  function agregarInstitucion(e) {
    e.preventDefault();

    if (
      !form.nombre_inst.trim() ||
      !form.dir_principal.trim() ||
      !form.id_sede.trim()
    ) {
      setError("Todos los campos son obligatorios");
      return;
    }

    axios
      .post("http://localhost:8000/instituciones", form)
      .then(() => {
        setForm({
          nombre_inst: "",
          jornada: "",
          dir_principal: "",
          id_sede: ""
        });

        setError("");
        cargarInstituciones();
      })
      .catch(() => setError("No se pudo crear la institución"));
  }

  // ===========================
  //  ELIMINAR
  // ===========================
  function eliminarInstitucion(id) {
    axios
      .delete(`http://localhost:8000/instituciones/${id}`)
      .then(() => cargarInstituciones())
      .catch(() => setError("Error al eliminar institución"));
  }

  // ===========================
  //  EDITAR
  // ===========================
  function activarEdicion(inst) {
    setEditId(inst.id_institucion);
    setEditForm({
      nombre_inst: inst.nombre_inst,
      jornada: inst.jornada,
      dir_principal: inst.dir_principal
    });
  }

  function handleEditChange(e) {
    setEditForm({ ...editForm, [e.target.name]: e.target.value });
  }

  function guardarEdicion(id) {
    axios
      .put(`http://localhost:8000/instituciones/${id}`, editForm)
      .then(() => {
        setEditId(null);
        cargarInstituciones();
      })
      .catch(() => setError("No se pudo editar institución"));
  }

  function cancelarEdicion() {
    setEditId(null);
  }

  return (
    <div className="instituciones-panel">
      <h2>Registrar Institución</h2>

      <form className="instituciones-form" onSubmit={agregarInstitucion}>
        <input
          type="text"
          name="nombre_inst"
          placeholder="Nombre institución"
          value={form.nombre_inst}
          onChange={(e) => setForm({ ...form, nombre_inst: e.target.value })}
          required
        />

        <input
          type="text"
          name="jornada"
          placeholder="Jornada"
          value={form.jornada}
          onChange={(e) => setForm({ ...form, jornada: e.target.value })}
        />

        <input
          type="text"
          name="dir_principal"
          placeholder="Dirección principal"
          value={form.dir_principal}
          onChange={(e) => setForm({ ...form, dir_principal: e.target.value })}
          required
        />

        {/* NUEVO CAMPO */}
        <input
          type="number"
          name="id_sede"
          placeholder="Número de sede inicial"
          value={form.id_sede}
          onChange={(e) => setForm({ ...form, id_sede: e.target.value })}
          required
        />

        <button type="submit" className="aulas-btn">
          Crear Institución
        </button>
      </form>

      {error && <div style={{ color: "red" }}>{error}</div>}

      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Jornada</th>
              <th>Dirección</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            {instituciones.map((inst) => (
              <tr key={inst.id_institucion}>
                <td>{inst.id_institucion}</td>

                <td>
                  {editId === inst.id_institucion ? (
                    <input
                      type="text"
                      name="nombre_inst"
                      value={editForm.nombre_inst}
                      onChange={handleEditChange}
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
                    />
                  ) : (
                    inst.jornada
                  )}
                </td>

                <td>
                  {editId === inst.id_institucion ? (
                    <input
                      type="text"
                      name="dir_principal"
                      value={editForm.dir_principal}
                      onChange={handleEditChange}
                    />
                  ) : (
                    inst.dir_principal
                  )}
                </td>

                <td>
                  {editId === inst.id_institucion ? (
                    <>
                      <button
                        className="btn-editar"
                        onClick={() => guardarEdicion(inst.id_institucion)}
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
                        onClick={() => activarEdicion(inst)}
                      >
                        Editar
                      </button>

                      <button
                        className="btn-eliminar"
                        onClick={() => eliminarInstitucion(inst.id_institucion)}
                      >
                        Eliminar
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}

            {instituciones.length === 0 && (
              <tr>
                <td colSpan={5}>No hay instituciones registradas</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Instituciones;
