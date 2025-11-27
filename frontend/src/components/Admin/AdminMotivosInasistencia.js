import React, { useState, useEffect } from "react";
import axios from "axios";

const BASE = "http://localhost:8000";

function AdminMotivosInasistencia() {
  const [motivos, setMotivos] = useState([]);
  const [nuevo, setNuevo] = useState("");
  const [editId, setEditId] = useState(null);
  const [editTxt, setEditTxt] = useState("");
  const [msg, setMsg] = useState("");

  const cargarMotivos = async () => {
    let resp = await axios.get(`${BASE}/admin/listar-motivos-inasistencia`);
    setMotivos(resp.data);
  };

  useEffect(() => {
    cargarMotivos();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    setMsg("");
    if (!nuevo.trim()) { setMsg("Escribe un motivo."); return; }
    try {
      let resp = await axios.post(`${BASE}/admin/agregar-motivo-inasistencia`, { descripcion: nuevo });
      setMsg(resp.data.msg);
      setNuevo("");
      cargarMotivos();
    } catch (err) {
      setMsg("Error al agregar motivo.");
    }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`${BASE}/admin/eliminar-motivo-inasistencia?id_motivo=${id}`);
      cargarMotivos();
      setMsg("Motivo eliminado.");
    } catch {
      setMsg("Error al eliminar motivo.");
    }
  };

  const handleStartEdit = (m) => {
    setEditId(m.id_motivo);
    setEditTxt(m.descripcion);
    setMsg("");
  };

  const handleEditSave = async (id) => {
    if (!editTxt.trim()) { setMsg("Escribe el motivo."); return; }
    try {
      await axios.put(`${BASE}/admin/modificar-motivo-inasistencia`, { id_motivo: id, descripcion: editTxt });
      setEditId(null);
      setEditTxt("");
      setMsg("Motivo actualizado.");
      cargarMotivos();
    } catch {
      setMsg("Error al modificar motivo.");
    }
  };

  const handleEditCancel = () => {
    setEditId(null);
    setEditTxt("");
    setMsg("");
  };

  return (
    <div className="instituciones-panel">
      <h2>Motivos de inasistencia</h2>
      <form onSubmit={handleAdd} className="instituciones-form">
        <input
          type="text"
          placeholder="Nuevo motivo"
          value={nuevo}
          onChange={e => setNuevo(e.target.value)}
          className="aulas-form-input"
        />
        <button type="submit" className="instituciones-btn">Agregar</button>
      </form>
      {msg && (
        <div style={{
          color: msg.toLowerCase().includes("error") ? "#c44e4e" : "#2563eb",
          marginBottom: "10px",
          fontWeight: 500
        }}>{msg}</div>
      )}
      <table className="instituciones-table" style={{marginTop: 14, maxWidth: 600}}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Motivo</th>
            <th style={{minWidth: 130}}>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {motivos.map(m => (
            <tr key={m.id_motivo}>
              <td>{m.id_motivo}</td>
              <td>
                {editId === m.id_motivo ? (
                  <input
                    value={editTxt}
                    onChange={e => setEditTxt(e.target.value)}
                    className="aulas-form-input"
                    style={{maxWidth:220}}
                  />
                ) : (
                  m.descripcion
                )}
              </td>
              <td>
                {editId === m.id_motivo ? (
                  <>
                    <button className="btn-editar" onClick={() => handleEditSave(m.id_motivo)}>Guardar</button>
                    <button className="btn-cancelar" onClick={handleEditCancel}>Cancelar</button>
                  </>
                ) : (
                  <>
                    <button className="btn-editar" onClick={() => handleStartEdit(m)}>Editar</button>
                    <button className="btn-eliminar" onClick={() => handleDelete(m.id_motivo)}>Eliminar</button>
                  </>
                )}
              </td>
            </tr>
          ))}
          {motivos.length === 0 &&
            <tr><td colSpan={3}>No hay motivos registrados</td></tr>
          }
        </tbody>
      </table>
    </div>
  );
}

export default AdminMotivosInasistencia;
