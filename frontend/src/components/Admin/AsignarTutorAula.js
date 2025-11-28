// src/components/AsignarTutorAula.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import "../../styles/AdminDashboard.css";

const BASE = "http://localhost:8000";

function AsignarTutorAula() {
  const [aulas, setAulas] = useState([]);
  const [personas, setPersonas] = useState([]);
  const [form, setForm] = useState({
    id_aula: "",
    id_persona: "",
    fecha_inicio: "",
  });
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [historial, setHistorial] = useState([]);
  const [loading, setLoading] = useState(false);

  // modal
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState(null); // "finalizar" | "cambiar"
  const [modalData, setModalData] = useState({
    id_tutor_aula_actual: null,
    motivo_cambio: "",
    fecha_fin_actual: "",
    id_persona_nuevo: "",
    fecha_inicio_nuevo: "",
  });
  const [filaSeleccionada, setFilaSeleccionada] = useState(null);

  useEffect(() => {
    axios.get(`${BASE}/aulas`)
      .then(r => setAulas(r.data || []))
      .catch(err => {
        console.error("Error cargando aulas:", err);
        setError("No se pudieron cargar las aulas");
      });

    axios.get(`${BASE}/personas`)
      .then(r => {
        const tutores = (r.data || []).filter(p => p.rol === "TUTOR");
        setPersonas(tutores);
      })
      .catch(err => {
        console.error("Error cargando tutores:", err);
        setError("No se pudieron cargar los tutores");
      });
  }, []);

  function cargarHistorial(idAula) {
    if (!idAula) {
      setHistorial([]);
      return;
    }
    axios.get(`${BASE}/historial-tutores-aula/${idAula}`)
      .then(r => setHistorial(r.data || []))
      .catch(err => {
        console.error("Error cargando historial:", err);
        setHistorial([]);
      });
  }

  function handleFormChange(e) {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
    if (name === "id_aula") {
      cargarHistorial(value);
      setMsg("");
      setError("");
    }
  }

  // Asignar tutor nuevo (sin tocar el modal)
  function asignarTutor(e) {
    e.preventDefault();
    setMsg("");
    setError("");

    if (!form.id_aula || !form.id_persona || !form.fecha_inicio) {
      setError("Debes seleccionar aula, tutor y fecha de inicio.");
      return;
    }

    setLoading(true);

    const payload = {
      id_aula: parseInt(form.id_aula, 10),
      id_persona: parseInt(form.id_persona, 10),
      fecha_inicio: form.fecha_inicio,
      motivo_cambio: null,
    };

    axios.post(`${BASE}/asignar-tutor-aula`, payload)
      .then(r => {
        setMsg(r.data.msg || "Tutor asignado correctamente.");
        cargarHistorial(form.id_aula);
        setForm(f => ({
          ...f,
          id_persona: "",
          fecha_inicio: "",
        }));
      })
      .catch(err => {
        console.error("AXIOS ERROR asignar tutor:", err);
        if (err.response?.data?.detail) {
          setError(err.response.data.detail);
        } else if (err.response?.data?.error) {
          setError(err.response.data.error);
        } else if (err.message) {
          setError("Error al asignar tutor: " + err.message);
        } else {
          setError("Error al asignar tutor.");
        }
      })
      .finally(() => setLoading(false));
  }

  // --------- MODAL ---------
  function abrirModalFinalizar(fila) {
    setFilaSeleccionada(fila);
    setModalMode("finalizar");
    setModalData({
      id_tutor_aula_actual: fila.id_tutor_aula,
      motivo_cambio: "",
      fecha_fin_actual: "",
      id_persona_nuevo: "",
      fecha_inicio_nuevo: "",
    });
    setModalOpen(true);
  }

  function abrirModalCambiar(fila) {
    if (!form.id_aula) {
      setError("Primero selecciona el aula arriba.");
      return;
    }
    setFilaSeleccionada(fila);
    setModalMode("cambiar");
    setModalData({
      id_tutor_aula_actual: fila.id_tutor_aula,
      motivo_cambio: "",
      fecha_fin_actual: "",
      id_persona_nuevo: "",
      fecha_inicio_nuevo: "",
    });
    setModalOpen(true);
  }

  function cerrarModal() {
    setModalOpen(false);
    setModalMode(null);
    setFilaSeleccionada(null);
    setModalData({
      id_tutor_aula_actual: null,
      motivo_cambio: "",
      fecha_fin_actual: "",
      id_persona_nuevo: "",
      fecha_inicio_nuevo: "",
    });
  }

  function handleModalChange(e) {
    const { name, value } = e.target;
    setModalData(m => ({ ...m, [name]: value }));
  }

  function confirmarModal() {
    if (!filaSeleccionada || !form.id_aula) {
      setError("Falta seleccionar aula o registro.");
      return;
    }
    setMsg("");
    setError("");

    if (!modalData.motivo_cambio.trim()) {
      setError("El motivo de cambio es obligatorio.");
      return;
    }

    if (modalMode === "finalizar") {
      setLoading(true);
      axios.put(
        `${BASE}/asignacion-tutor/${modalData.id_tutor_aula_actual}/fin`,
        null,
        {
          params: {
            fecha_fin: modalData.fecha_fin_actual || null,
            motivo_cambio: modalData.motivo_cambio,
          },
        }
      )
        .then(r => {
          setMsg(r.data.msg || "Asignación de tutor finalizada.");
          cargarHistorial(form.id_aula);
          cerrarModal();
        })
        .catch(err => {
          console.error("Error al finalizar asignación:", err);
          setError(err.response?.data?.detail || "Error al finalizar asignación.");
        })
        .finally(() => setLoading(false));
    } else if (modalMode === "cambiar") {
      if (!modalData.id_persona_nuevo || !modalData.fecha_inicio_nuevo) {
        setError("Debes seleccionar nuevo tutor y su fecha de inicio.");
        return;
      }
      setLoading(true);
      const payload = {
        id_aula: parseInt(form.id_aula, 10),
        id_persona: parseInt(modalData.id_persona_nuevo, 10),
        fecha_inicio: modalData.fecha_inicio_nuevo,
        motivo_cambio: modalData.motivo_cambio,
        id_tutor_aula_actual: modalData.id_tutor_aula_actual,
        fecha_fin_actual: modalData.fecha_fin_actual || null,
      };
      axios.post(`${BASE}/cambiar-tutor-aula`, payload)
        .then(r => {
          setMsg(r.data.msg || "Tutor cambiado correctamente.");
          cargarHistorial(form.id_aula);
          cerrarModal();
        })
        .catch(err => {
          console.error("Error al cambiar tutor:", err);
          setError(err.response?.data?.detail || "Error al cambiar tutor.");
        })
        .finally(() => setLoading(false));
    }
  }

  return (
    <div className="instituciones-panel">
      <h2>Asignar / Gestionar Tutor de Aula</h2>

      {/* Formulario para asignar tutor nuevo */}
      <form className="instituciones-form" onSubmit={asignarTutor}>
        <select
          className="aulas-form-input"
          name="id_aula"
          value={form.id_aula}
          onChange={handleFormChange}
          required
          disabled={loading}
        >
          <option value="">Selecciona un aula</option>
          {aulas.map(a => (
            <option key={a.id_aula} value={a.id_aula}>
              Aula #{a.id_aula} - {a.grado}° - Inst {a.id_institucion} (Sede {a.id_sede})
            </option>
          ))}
        </select>

        <select
          className="aulas-form-input"
          name="id_persona"
          value={form.id_persona}
          onChange={handleFormChange}
          required
          disabled={loading}
        >
          <option value="">Selecciona un tutor</option>
          {personas.map(p => (
            <option key={p.id_persona} value={p.id_persona}>
              {p.nombre} ({p.correo})
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
          disabled={loading}
        />

        <button
          type="submit"
          className="aulas-btn"
          disabled={loading || !form.id_aula || !form.id_persona || !form.fecha_inicio}
        >
          {loading ? "Procesando..." : "Asignar Tutor"}
        </button>
      </form>

      {msg && (
        <div style={{
          color: "green",
          marginTop: "10px",
          background: "#d4edda",
          borderRadius: "4px",
          padding: "8px",
        }}>
          {msg}
        </div>
      )}

      {error && (
        <div style={{
          color: "red",
          marginTop: "10px",
          background: "#f8d7da",
          borderRadius: "4px",
          padding: "8px",
        }}>
          {error}
        </div>
      )}

      <h3>Historial de tutores del aula</h3>
      <div className="table-responsive">
        <table className="aulas-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Tutor</th>
              <th>Correo</th>
              <th>Inicio</th>
              <th>Fin</th>
              <th>Motivo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {historial.map(h => (
              <tr key={h.id_tutor_aula}>
                <td>{h.id_tutor_aula}</td>
                <td>{h.nombre_tutor}</td>
                <td>{h.correo_tutor}</td>
                <td>{h.fecha_inicio || "-"}</td>
                <td>{h.fecha_fin || "[Activo]"}</td>
                <td>{h.motivo_cambio || "-"}</td>
                <td>
                  {!h.fecha_fin && (
                    <>
                      <button
                        type="button"
                        className="btn-editar"
                        onClick={() => abrirModalFinalizar(h)}
                      >
                        Finalizar
                      </button>
                      <button
                        type="button"
                        className="btn-editar"
                        style={{ marginLeft: "6px", backgroundColor: "#f0ad4e" }}
                        onClick={() => abrirModalCambiar(h)}
                      >
                        Cambiar
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
            {historial.length === 0 && (
              <tr>
                <td colSpan={7} style={{ textAlign: "center", color: "#666" }}>
                  Selecciona un aula para ver historial
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Modal */}
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
                ? "Finalizar tutor del aula"
                : "Cambiar tutor del aula"}
            </h3>

            <p><strong>Tutor actual:</strong> {filaSeleccionada?.nombre_tutor}</p>

            <div className="modal-field">
              <label>Motivo del cambio/finalización</label>
              <input
                type="text"
                name="motivo_cambio"
                value={modalData.motivo_cambio}
                onChange={handleModalChange}
                className="aulas-form-input"
              />
            </div>

            <div className="modal-field">
              <label>Fecha de fin del tutor actual</label>
              <input
                type="date"
                name="fecha_fin_actual"
                value={modalData.fecha_fin_actual}
                onChange={handleModalChange}
                className="aulas-form-input"
              />
              <small>Si la dejas vacía se usará la fecha actual.</small>
            </div>

            {modalMode === "cambiar" && (
              <>
                <div className="modal-field">
                  <label>Nuevo tutor</label>
                  <select
                    name="id_persona_nuevo"
                    value={modalData.id_persona_nuevo}
                    onChange={handleModalChange}
                    className="aulas-form-input"
                  >
                    <option value="">Selecciona nuevo tutor</option>
                    {personas.map(p => (
                      <option key={p.id_persona} value={p.id_persona}>
                        {p.nombre} ({p.correo})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="modal-field">
                  <label>Fecha de inicio del nuevo tutor</label>
                  <input
                    type="date"
                    name="fecha_inicio_nuevo"
                    value={modalData.fecha_inicio_nuevo}
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

export default AsignarTutorAula;
