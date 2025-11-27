// src/components/Admin/Sedes.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

function Sedes() {
  const [sedes, setSedes] = useState([]);
  const [form, setForm] = useState({
    id_institucion: "",
    direccion: "",
    es_principal: "N"
  });

  const [editPk, setEditPk] = useState(null); // { id_institucion, id_sede }
  const [editForm, setEditForm] = useState({
    id_institucion: "",
    direccion: "",
    es_principal: "N"
  });

  const [error, setError] = useState("");

  useEffect(() => {
    cargarSedes();
  }, []);

  function cargarSedes() {
    axios
      .get("http://localhost:8000/sedes")
      .then((r) => setSedes(r.data))
      .catch(() => setError("Error al cargar sedes"));
  }

  // ===========================
  //  AGREGAR SEDE
  // ===========================
  function agregarSede(e) {
    e.preventDefault();
    if (!form.id_institucion.trim() || !form.direccion.trim()) {
      setError("Todos los campos son obligatorios");
      return;
    }

    axios
      .post("http://localhost:8000/sedes", form)
      .then(() => {
        setForm({ id_institucion: "", direccion: "", es_principal: "N" });
        setError("");
        cargarSedes();
      })
      .catch(() => setError("No se pudo agregar la sede"));
  }

  // ===========================
  //  ELIMINAR SEDE
  // ===========================
  function eliminarSede(id_institucion, id_sede) {
    axios
      .delete(
        `http://localhost:8000/sedes/${id_institucion}/${id_sede}`
      )
      .then(() => cargarSedes())
      .catch(() => setError("Error al eliminar sede"));
  }

  // ===========================
  //  ACTIVAR EDICIÓN
  // ===========================
  function activarEdicion(sede) {
    setEditPk({
      id_institucion: sede.id_institucion,
      id_sede: sede.id_sede
    });

    setEditForm({
      id_institucion: sede.id_institucion,
      direccion: sede.direccion,
      es_principal: sede.es_principal
    });
  }

  function handleEditChange(e) {
    const { name, value } = e.target;
    setEditForm((f) => ({ ...f, [name]: value }));
  }

  // ===========================
  //  GUARDAR EDICIÓN
  // ===========================
  function guardarEdicion() {
    axios
      .put(
        `http://localhost:8000/sedes/${editPk.id_institucion}/${editPk.id_sede}`,
        editForm
      )
      .then(() => {
        setEditPk(null);
        setEditForm({
          id_institucion: "",
          direccion: "",
          es_principal: "N"
        });
        cargarSedes();
      })
      .catch(() => setError("No se pudo editar la sede"));
  }

  function cancelarEdicion() {
    setEditPk(null);
    setEditForm({
      id_institucion: "",
      direccion: "",
      es_principal: "N"
    });
  }

  return (
    <div className="sedes-panel">
      <h2>Gestión de Sedes</h2>

      <form className="sedes-form" onSubmit={agregarSede}>
        <input
          type="text"
          name="id_institucion"
          placeholder="ID Institución"
          value={form.id_institucion}
          onChange={(e) =>
            setForm({ ...form, id_institucion: e.target.value })
          }
          required
        />

        <input
          type="text"
          name="direccion"
          placeholder="Dirección"
          value={form.direccion}
          onChange={(e) =>
            setForm({ ...form, direccion: e.target.value })
          }
          required
        />

        <select
          name="es_principal"
          value={form.es_principal}
          onChange={(e) =>
            setForm({ ...form, es_principal: e.target.value })
          }
        >
          <option value="N">No principal</option>
          <option value="S">Principal</option>
        </select>

        <button type="submit" className="sedes-btn">
          Agregar Sede
        </button>
      </form>

      {error && <div style={{ color: "red" }}>{error}</div>}

      <table className="sedes-table">
        <thead>
          <tr>
            <th>ID_SEDE</th>
            <th>ID_INSTITUCION</th>
            <th>DIRECCIÓN</th>
            <th>PRINCIPAL</th>
            <th>Acciones</th>
          </tr>
        </thead>

        <tbody>
          {sedes.map((sede) => (
            <tr key={`${sede.id_institucion}-${sede.id_sede}`}>
              <td>{sede.id_sede}</td>

              <td>
                {editPk &&
                editPk.id_institucion === sede.id_institucion &&
                editPk.id_sede === sede.id_sede ? (
                  <input
                    type="text"
                    name="id_institucion"
                    value={editForm.id_institucion}
                    onChange={handleEditChange}
                  />
                ) : (
                  sede.id_institucion
                )}
              </td>

              <td>
                {editPk &&
                editPk.id_institucion === sede.id_institucion &&
                editPk.id_sede === sede.id_sede ? (
                  <input
                    type="text"
                    name="direccion"
                    value={editForm.direccion}
                    onChange={handleEditChange}
                  />
                ) : (
                  sede.direccion
                )}
              </td>

              <td>
                {editPk &&
                editPk.id_institucion === sede.id_institucion &&
                editPk.id_sede === sede.id_sede ? (
                  <select
                    name="es_principal"
                    value={editForm.es_principal}
                    onChange={handleEditChange}
                  >
                    <option value="N">No principal</option>
                    <option value="S">Principal</option>
                  </select>
                ) : sede.es_principal === "S" ? (
                  "Principal"
                ) : (
                  "No principal"
                )}
              </td>

              <td>
                {editPk &&
                editPk.id_institucion === sede.id_institucion &&
                editPk.id_sede === sede.id_sede ? (
                  <>
                    <button className="btn-editar" onClick={guardarEdicion}>
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
                      onClick={() => activarEdicion(sede)}
                    >
                      Editar
                    </button>

                    <button
                      className="btn-eliminar"
                      onClick={() =>
                        eliminarSede(sede.id_institucion, sede.id_sede)
                      }
                    >
                      Eliminar
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}

          {sedes.length === 0 && (
            <tr>
              <td colSpan={5}>No hay sedes registradas</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default Sedes;