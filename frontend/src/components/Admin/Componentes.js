// src/components/Componentes.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

const BASE = "http://localhost:8000";

function Componentes() {
  const [componentes, setComponentes] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [form, setForm] = useState({
    nombre: "",
    porcentaje: "",
    tipo_programa: "",
    id_periodo: "",
  });
  const [msg, setMsg] = useState("");
  const [editId, setEditId] = useState(null);
  const [editForm, setEditForm] = useState({
    nombre: "",
    porcentaje: "",
    tipo_programa: "",
    id_periodo: "",
  });

  useEffect(() => {
    cargarComponentes();
    cargarPeriodos();
  }, []);

  function cargarComponentes() {
    axios
      .get(`${BASE}/componentes`)
      .then((r) => setComponentes(r.data || []))
      .catch(() => setMsg("Error al cargar componentes"));
  }

  function cargarPeriodos() {
    axios
      .get(`${BASE}/admin/listar-periodos`)
      .then((r) => setPeriodos(r.data || []))
      .catch(() => setMsg("Error al cargar períodos"));
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  }

  function handleEditChange(e) {
    const { name, value } = e.target;
    setEditForm((f) => ({ ...f, [name]: value }));
  }

  function agregarComponente(e) {
    e.preventDefault();
    setMsg("");

    if (!form.id_periodo) {
      setMsg("Debes seleccionar un período");
      return;
    }
    if (!form.tipo_programa) {
      setMsg("Debes seleccionar el tipo de programa");
      return;
    }

    const payload = {
      ...form,
      id_periodo: Number(form.id_periodo),
      porcentaje: Number(form.porcentaje),
      // tipo_programa se guarda tal cual: INSIDECLASSROOM / OUTSIDECLASSROOM
    };

    axios
      .post(`${BASE}/componentes`, payload)
      .then((r) => {
        setMsg(r.data.msg);
        cargarComponentes();
        setForm({
          nombre: "",
          porcentaje: "",
          tipo_programa: "",
          id_periodo: "",
        });
      })
      .catch((err) => {
        setMsg(err.response?.data?.detail || "Error al crear componente");
      });
  }

  function activarEdicion(c) {
    setEditId(c.id_componente);
    setEditForm({
      nombre: c.nombre,
      porcentaje: c.porcentaje,
      tipo_programa: c.tipo_programa || "",
      id_periodo: c.id_periodo ? String(c.id_periodo) : "",
    });
  }

  function cancelarEdicion() {
    setEditId(null);
    setEditForm({
      nombre: "",
      porcentaje: "",
      tipo_programa: "",
      id_periodo: "",
    });
  }

  function guardarEdicion(id) {
    setMsg("");

    if (!editForm.id_periodo) {
      setMsg("Debes seleccionar un período");
      return;
    }
    if (!editForm.tipo_programa) {
      setMsg("Debes seleccionar el tipo de programa");
      return;
    }

    const payload = {
      ...editForm,
      id_periodo: Number(editForm.id_periodo),
      porcentaje: Number(editForm.porcentaje),
    };

    axios
      .put(`${BASE}/componentes/${id}`, payload)
      .then((r) => {
        setMsg(r.data.msg);
        setEditId(null);
        setEditForm({
          nombre: "",
          porcentaje: "",
          tipo_programa: "",
          id_periodo: "",
        });
        cargarComponentes();
      })
      .catch((err) => {
        setMsg(err.response?.data?.detail || "Error al actualizar componente");
      });
  }

  function eliminarComponente(id) {
    if (!window.confirm("¿Eliminar este componente?")) return;
    setMsg("");
    axios
      .delete(`${BASE}/componentes/${id}`)
      .then((r) => {
        setMsg(r.data.msg);
        cargarComponentes();
      })
      .catch((err) => {
        setMsg(err.response?.data?.detail || "Error al eliminar componente");
      });
  }

  function labelTipo(tipo) {
    if (tipo === "INSIDECLASSROOM") return "Inside Classroom";
    if (tipo === "OUTSIDECLASSROOM") return "Outside Classroom";
    return "N/A";
  }

  return (
    <div className="instituciones-panel">
      <h2>Registrar Componente de Nota</h2>

      <form className="instituciones-form" onSubmit={agregarComponente}>
        <select
          className="aulas-form-input"
          name="id_periodo"
          value={form.id_periodo}
          onChange={handleFormChange}
          required
        >
          <option value="">Seleccione período</option>
          {periodos.map((p) => (
            <option value={p.id_periodo} key={p.id_periodo}>
              {p.nombre}
            </option>
          ))}
        </select>

        <input
          className="aulas-form-input"
          name="nombre"
          value={form.nombre}
          onChange={handleFormChange}
          placeholder="Nombre componente"
          required
        />

        <input
          className="aulas-form-input"
          type="number"
          name="porcentaje"
          value={form.porcentaje}
          min="0"
          max="100"
          step="0.1"
          onChange={handleFormChange}
          placeholder="Porcentaje"
          required
        />

        <select
          className="aulas-form-input"
          name="tipo_programa"
          value={form.tipo_programa}
          onChange={handleFormChange}
          required
        >
          <option value="">Tipo de programa</option>
          <option value="INSIDECLASSROOM">Inside Classroom</option>
          <option value="OUTSIDECLASSROOM">Outside Classroom</option>
        </select>

        <button type="submit" className="aulas-btn">
          Registrar Componente
        </button>
      </form>

      {msg && (
        <div
          style={{
            color: msg.toLowerCase().includes("error") ? "red" : "green",
            marginBottom: "10px",
          }}
        >
          {msg}
        </div>
      )}

      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>%</th>
              <th>Tipo programa</th>
              <th>Período</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {componentes.map((c) => (
              <tr key={c.id_componente}>
                <td>{c.id_componente}</td>
                <td>
                  {editId === c.id_componente ? (
                    <input
                      className="aulas-form-input"
                      name="nombre"
                      value={editForm.nombre}
                      onChange={handleEditChange}
                    />
                  ) : (
                    c.nombre
                  )}
                </td>
                <td>
                  {editId === c.id_componente ? (
                    <input
                      className="aulas-form-input"
                      type="number"
                      name="porcentaje"
                      value={editForm.porcentaje}
                      min="0"
                      max="100"
                      step="0.1"
                      onChange={handleEditChange}
                    />
                  ) : (
                    c.porcentaje
                  )}
                </td>
                <td>
                  {editId === c.id_componente ? (
                    <select
                      className="aulas-form-input"
                      name="tipo_programa"
                      value={editForm.tipo_programa}
                      onChange={handleEditChange}
                      required
                    >
                      <option value="">Tipo de programa</option>
                      <option value="INSIDECLASSROOM">Inside Classroom</option>
                      <option value="OUTSIDECLASSROOM">Outside Classroom</option>
                    </select>
                  ) : (
                    labelTipo(c.tipo_programa)
                  )}
                </td>
                <td>{c.periodo_nombre || "N/A"}</td>
                <td>
                  {editId === c.id_componente ? (
                    <>
                      <button
                        type="button"
                        className="btn-editar"
                        onClick={() => guardarEdicion(c.id_componente)}
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
                        onClick={() => activarEdicion(c)}
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        className="btn-eliminar"
                        onClick={() => eliminarComponente(c.id_componente)}
                      >
                        Eliminar
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
            {componentes.length === 0 && (
              <tr>
                <td colSpan={6}>No hay componentes registrados</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Componentes;
