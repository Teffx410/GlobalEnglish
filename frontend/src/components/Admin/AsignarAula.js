// src/components/AsignarAula.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

const BASE = "http://localhost:8000";

function AsignarAula() {
  const [estudiantes, setEstudiantes] = useState([]);
  const [instituciones, setInstituciones] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [aulas, setAulas] = useState([]);
  const [estudiantesAula, setEstudiantesAula] = useState([]);
  const [form, setForm] = useState({
    id_estudiante: "",
    id_institucion: "",
    id_sede: "",
    id_aula: "",
    fecha_inicio: "",
    fecha_fin: "",       // NUEVO
  });
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  // modal cambio / finalizar
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState(null); // "finalizar" | "cambiar"
  const [filaSeleccionada, setFilaSeleccionada] = useState(null);
  const [modalData, setModalData] = useState({
    fecha_fin_actual: "",
    id_aula_destino: "",
    fecha_inicio_nueva: "",
    fecha_fin_nueva: "",   // NUEVO
  });

  useEffect(() => {
    axios.get(`${BASE}/estudiantes`).then(r => setEstudiantes(r.data || []));
    axios.get(`${BASE}/instituciones`).then(r => setInstituciones(r.data || []));
    axios.get(`${BASE}/aulas`).then(r => setAulas(r.data || []));
  }, []);

  function cargarSedes(id_institucion) {
    if (!id_institucion) {
      setSedes([]);
      return;
    }
    axios
      .get(`${BASE}/sedes`)
      .then(r => {
        setSedes(
          (r.data || []).filter(s => s.id_institucion === Number(id_institucion))
        );
      })
      .catch(() => setSedes([]));
  }

  function cargarEstudiantesAula(id_aula) {
    if (!id_aula) {
      setEstudiantesAula([]);
      return;
    }
    axios
      .get(`${BASE}/estudiantes-aula/${id_aula}`)
      .then(r => setEstudiantesAula(r.data || []))
      .catch(() => setEstudiantesAula([]));
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
    setMsg("");

    if (name === "id_institucion") {
      setForm(f => ({
        ...f,
        id_institucion: value,
        id_sede: "",
        id_aula: "",
      }));
      setEstudiantesAula([]);
      cargarSedes(value);
    }

    if (name === "id_sede") {
      setForm(f => ({ ...f, id_sede: value, id_aula: "" }));
      setEstudiantesAula([]);
    }

    if (name === "id_aula") {
      setForm(f => ({ ...f, id_aula: value }));
      cargarEstudiantesAula(value);
    }
  }

  function aulasFiltradas() {
    if (!form.id_institucion || !form.id_sede) return [];
    return aulas.filter(
      a =>
        a.id_institucion === Number(form.id_institucion) &&
        a.id_sede === Number(form.id_sede)
    );
  }

  async function asignar(e) {
    e.preventDefault();
    setMsg("");
    if (!form.id_estudiante || !form.id_aula || !form.fecha_inicio) {
      setMsg("Selecciona estudiante, aula y fecha de inicio.");
      return;
    }
    try {
      setLoading(true);
      await axios.post(`${BASE}/asignar-estudiante-aula`, {
        id_estudiante: Number(form.id_estudiante),
        id_aula: Number(form.id_aula),
        fecha_inicio: form.fecha_inicio,
        fecha_fin: form.fecha_fin || null,
      });
      setMsg("Estudiante asignado correctamente");
      cargarEstudiantesAula(form.id_aula);
      setForm(f => ({
        ...f,
        id_estudiante: "",
        fecha_inicio: "",
        fecha_fin: "",
      }));
    } catch (err) {
      if (err.response?.data?.detail) {
        setMsg("Error: " + err.response.data.detail);
      } else if (err.response?.data?.error) {
        setMsg("Error: " + err.response.data.error);
      } else {
        setMsg("Error al asignar estudiante");
      }
    } finally {
      setLoading(false);
    }
  }

  // ----- Modal -----

  function abrirModalFinalizar(fila) {
    setFilaSeleccionada(fila);
    setModalMode("finalizar");
    setModalData({
      fecha_fin_actual: "",
      id_aula_destino: "",
      fecha_inicio_nueva: "",
      fecha_fin_nueva: "",
    });
    setModalOpen(true);
  }

  function abrirModalCambiar(fila) {
    if (!form.id_aula) {
      setMsg("Primero selecciona el aula origen arriba.");
      return;
    }
    setFilaSeleccionada(fila);
    setModalMode("cambiar");
    setModalData({
      fecha_fin_actual: "",
      id_aula_destino: "",
      fecha_inicio_nueva: "",
      fecha_fin_nueva: "",
    });
    setModalOpen(true);
  }

  function cerrarModal() {
    setModalOpen(false);
    setModalMode(null);
    setFilaSeleccionada(null);
    setModalData({
      fecha_fin_actual: "",
      id_aula_destino: "",
      fecha_inicio_nueva: "",
      fecha_fin_nueva: "",
    });
  }

  function handleModalChange(e) {
    const { name, value } = e.target;
    setModalData(m => ({ ...m, [name]: value }));
  }

  async function confirmarModal() {
    if (!filaSeleccionada) {
      setMsg("No hay estudiante seleccionado.");
      return;
    }
    setMsg("");

    if (modalMode === "finalizar") {
      try {
        setLoading(true);
        await axios.put(
          `${BASE}/hist-aula-estudiante/${filaSeleccionada.id_hist_aula_est}/fin`,
          null,
          { params: { fecha_fin: modalData.fecha_fin_actual || null } }
        );
        setMsg("Asignación finalizada.");
        cargarEstudiantesAula(form.id_aula);
        cerrarModal();
      } catch (err) {
        setMsg(
          err.response?.data?.detail || "Error al finalizar asignación."
        );
      } finally {
        setLoading(false);
      }
    } else if (modalMode === "cambiar") {
      if (!modalData.id_aula_destino || !modalData.fecha_inicio_nueva) {
        setMsg("Debes seleccionar aula destino y fecha de inicio.");
        return;
      }
      try {
        setLoading(true);
        await axios.post(`${BASE}/cambiar-estudiante-aula`, {
          id_hist_aula_est: filaSeleccionada.id_hist_aula_est,
          id_aula_origen: Number(form.id_aula),
          id_aula_destino: Number(modalData.id_aula_destino),
          id_estudiante: filaSeleccionada.id_estudiante,
          fecha_fin_actual: modalData.fecha_fin_actual || null,
          fecha_inicio_nueva: modalData.fecha_inicio_nueva,
          fecha_fin_nueva: modalData.fecha_fin_nueva || null,
        });
        setMsg("Estudiante movido de aula correctamente.");
        cargarEstudiantesAula(form.id_aula);
        cerrarModal();
      } catch (err) {
        setMsg(
          err.response?.data?.detail || "Error al cambiar estudiante de aula."
        );
      } finally {
        setLoading(false);
      }
    }
  }

  return (
    <div className="instituciones-panel">
      <h2>Asignar / Gestionar Estudiantes por Aula</h2>
      <form className="instituciones-form" onSubmit={asignar}>
        <select
          className="aulas-form-input"
          name="id_estudiante"
          value={form.id_estudiante}
          onChange={handleFormChange}
          required
        >
          <option value="">Estudiante</option>
          {estudiantes.map(est => (
            <option key={est.id_estudiante} value={est.id_estudiante}>
              {est.nombres} {est.apellidos} (ID: {est.id_estudiante})
            </option>
          ))}
        </select>

        <select
          className="aulas-form-input"
          name="id_institucion"
          value={form.id_institucion}
          onChange={handleFormChange}
          required
        >
          <option value="">Institución</option>
          {instituciones.map(i => (
            <option key={i.id_institucion} value={i.id_institucion}>
              {i.nombre_inst}
            </option>
          ))}
        </select>

        <select
          className="aulas-form-input"
          name="id_sede"
          value={form.id_sede}
          onChange={handleFormChange}
          required
          disabled={!form.id_institucion}
        >
          <option value="">Sede</option>
          {sedes.map(s => (
            <option key={s.id_sede} value={s.id_sede}>
              {s.direccion} ({s.id_sede})
            </option>
          ))}
        </select>

        <select
          className="aulas-form-input"
          name="id_aula"
          value={form.id_aula}
          onChange={handleFormChange}
          required
          disabled={!form.id_sede}
        >
          <option value="">Aula</option>
          {aulasFiltradas().map(a => (
            <option key={a.id_aula} value={a.id_aula}>
              Grado {a.grado} ({a.id_aula})
            </option>
          ))}
        </select>

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
          placeholder="Fecha fin (opcional)"
        />

        <button
          type="submit"
          className="aulas-btn"
          disabled={
            loading || !form.id_estudiante || !form.id_aula || !form.fecha_inicio
          }
        >
          {loading ? "Asignando..." : "Asignar"}
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

      <h3>Estudiantes del aula seleccionada</h3>
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID Est.</th>
              <th>Nombre</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {estudiantesAula.map(e => (
              <tr key={e.id_hist_aula_est}>
                <td>{e.id_estudiante}</td>
                <td>
                  {e.nombres} {e.apellidos}
                </td>
                <td>{e.fecha_inicio || "-"}</td>
                <td>{e.fecha_fin || "[Activo]"}</td>
                <td>
                  {!e.fecha_fin && (
                    <>
                      <button
                        type="button"
                        className="btn-editar"
                        onClick={() => abrirModalFinalizar(e)}
                      >
                        Finalizar
                      </button>
                      <button
                        type="button"
                        className="btn-cambiar"
                        onClick={() => abrirModalCambiar(e)}
                      >
                        Cambiar
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
            {estudiantesAula.length === 0 && (
              <tr>
                <td colSpan={5} style={{ textAlign: "center", color: "#666" }}>
                  Selecciona un aula para ver sus estudiantes
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
          }}
        >
          <div
            style={{
              background: "#fff",
              padding: "20px",
              borderRadius: "8px",
              minWidth: "320px",
              maxWidth: "480px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
            }}
          >
            <h3 style={{ marginTop: 0 }}>
              {modalMode === "finalizar"
                ? "Finalizar asignación de estudiante"
                : "Cambiar estudiante de aula"}
            </h3>

            <p>
              <strong>Estudiante:</strong>{" "}
              {filaSeleccionada?.nombres} {filaSeleccionada?.apellidos}
            </p>

            <div className="modal-field">
              <label>Fecha de fin en el aula actual</label>
              <input
                type="date"
                name="fecha_fin_actual"
                value={modalData.fecha_fin_actual}
                onChange={handleModalChange}
                className="aulas-form-input"
              />
              <small>Si se deja vacío se usará la fecha actual.</small>
            </div>

            {modalMode === "cambiar" && (
              <>
                <div className="modal-field">
                  <label>Aula destino</label>
                  <select
                    name="id_aula_destino"
                    value={modalData.id_aula_destino}
                    onChange={handleModalChange}
                    className="aulas-form-input"
                  >
                    <option value="">Seleccione aula destino</option>
                    {aulas.map(a => (
                      <option key={a.id_aula} value={a.id_aula}>
                        Grado {a.grado} ({a.id_aula}) – Inst {a.id_institucion} Sede{" "}
                        {a.id_sede}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="modal-field">
                  <label>Fecha inicio en aula destino</label>
                  <input
                    type="date"
                    name="fecha_inicio_nueva"
                    value={modalData.fecha_inicio_nueva}
                    onChange={handleModalChange}
                    className="aulas-form-input"
                  />
                </div>
                <div className="modal-field">
                  <label>Fecha fin en aula destino (opcional)</label>
                  <input
                    type="date"
                    name="fecha_fin_nueva"
                    value={modalData.fecha_fin_nueva}
                    onChange={handleModalChange}
                    className="aulas-form-input"
                  />
                </div>
              </>
            )}

            <div style={{ marginTop: "15px", textAlign: "right" }}>
              <button
                type="button"
                className="aulas-btn"
                style={{ marginRight: "8px", backgroundColor: "#ccc", color: "#000" }}
                onClick={cerrarModal}
              >
                Cancelar
              </button>
              <button
                type="button"
                className="aulas-btn"
                onClick={confirmarModal}
                disabled={loading}
              >
                {loading ? "Guardando..." : "Confirmar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AsignarAula;
