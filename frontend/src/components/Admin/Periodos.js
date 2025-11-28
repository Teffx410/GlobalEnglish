import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

const BASE = "http://localhost:8000";

function Periodos() {
  const [periodos, setPeriodos] = useState([]);
  const [form, setForm] = useState({ nombre: "", fecha_inicio: "", fecha_fin: "" });
  const [msg, setMsg] = useState("");
  const [editId, setEditId] = useState(null);
  const [editForm, setEditForm] = useState({ nombre: "", fecha_inicio: "", fecha_fin: "" });

  useEffect(() => {
    cargarPeriodos();
  }, []);

  function cargarPeriodos() {
    axios
      .get(`${BASE}/periodos`)
      .then((r) => setPeriodos(r.data || []))
      .catch(() => setMsg("Error al cargar periodos"));
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  }

  function handleEditChange(e) {
    const { name, value } = e.target;
    setEditForm((f) => ({ ...f, [name]: value }));
  }

  function agregarPeriodo(e) {
    e.preventDefault();
    setMsg("");
    axios
      .post(`${BASE}/periodos`, form)
      .then((r) => {
        setMsg(r.data.msg);
        cargarPeriodos();
        setForm({ nombre: "", fecha_inicio: "", fecha_fin: "" });
      })
      .catch((err) => setMsg(err.response?.data?.detail || "Error al crear periodo"));
  }

  function activarEdicion(p) {
    setEditId(p.id_periodo);
    setEditForm({
      nombre: p.nombre,
      fecha_inicio: p.fecha_inicio || "",
      fecha_fin: p.fecha_fin || "",
    });
  }

  function cancelarEdicion() {
    setEditId(null);
    setEditForm({ nombre: "", fecha_inicio: "", fecha_fin: "" });
  }

  function guardarPeriodo(id) {
    setMsg("");
    axios
      .put(`${BASE}/periodos/${id}`, editForm)
      .then((r) => {
        setMsg(r.data.msg);
        setEditId(null);
        setEditForm({ nombre: "", fecha_inicio: "", fecha_fin: "" });
        cargarPeriodos();
      })
      .catch((err) => setMsg(err.response?.data?.detail || "Error al actualizar periodo"));
  }

  function eliminarPeriodo(id) {
    if (!window.confirm("¿Eliminar este periodo?")) return;
    setMsg("");
    axios
      .delete(`${BASE}/periodos/${id}`)
      .then((r) => {
        setMsg(r.data.msg);
        cargarPeriodos();
      })
      .catch((err) => setMsg(err.response?.data?.detail || "Error al eliminar periodo"));
  }

  return (
    <div className="instituciones-panel">
      <h2>Registrar Periodo</h2>
      <form className="instituciones-form" onSubmit={agregarPeriodo}>
        <input
          className="aulas-form-input"
          name="nombre"
          value={form.nombre}
          onChange={handleFormChange}
          placeholder="Nombre del periodo"
          required
        />
        <input
          className="aulas-form-input"
          type="date"
          name="fecha_inicio"
          value={form.fecha_inicio}
          onChange={handleFormChange}
          required
        />
        <input
          className="aulas-form-input"
          type="date"
          name="fecha_fin"
          value={form.fecha_fin}
          onChange={handleFormChange}
          required
        />
        <button type="submit" className="aulas-btn">
          Registrar Periodo
        </button>
      </form>

      {msg && (
        <div style={{ color: msg.toLowerCase().includes("error") ? "red" : "green", marginBottom: "10px" }}>
          {msg}
        </div>
      )}

      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {periodos.map((p) => (
              <tr key={p.id_periodo}>
                <td>{p.id_periodo}</td>
                <td>
                  {editId === p.id_periodo ? (
                    <input
                      className="aulas-form-input"
                      name="nombre"
                      value={editForm.nombre}
                      onChange={handleEditChange}
                    />
                  ) : (
                    p.nombre
                  )}
                </td>
                <td>
                  {editId === p.id_periodo ? (
                    <input
                      className="aulas-form-input"
                      type="date"
                      name="fecha_inicio"
                      value={editForm.fecha_inicio}
                      onChange={handleEditChange}
                    />
                  ) : (
                    p.fecha_inicio
                  )}
                </td>
                <td>
                  {editId === p.id_periodo ? (
                    <input
                      className="aulas-form-input"
                      type="date"
                      name="fecha_fin"
                      value={editForm.fecha_fin}
                      onChange={handleEditChange}
                    />
                  ) : (
                    p.fecha_fin
                  )}
                </td>
                <td>
                  {editId === p.id_periodo ? (
                    <>
                      <button
                        type="button"
                        className="btn-editar"
                        onClick={() => guardarPeriodo(p.id_periodo)}
                      >
                        Guardar
                      </button>
                      <button
                        type="button"
                        className="btn-cancelar"
                        onClick={cancelarEdicion}
                      >
                        Cancelar
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        type="button"
                        className="btn-editar"
                        onClick={() => activarEdicion(p)}
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        className="btn-eliminar"
                        onClick={() => eliminarPeriodo(p.id_periodo)}
                      >
                        Eliminar
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
            {periodos.length === 0 && (
              <tr>
                <td colSpan={5}>No hay periodos registrados</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Periodos;
